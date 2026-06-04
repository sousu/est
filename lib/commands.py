"""est サブコマンド実装"""
import os
import re
import subprocess
import sys
import time
from urllib.parse import unquote
from . import config as cfg
from . import docker
from . import builder

# 全genreをmergeする作業db (org の casket_work 相当) と公開先
CASKET  = "/casket"
MERGED  = "/casket_merged"
PUBLISH = "/htdocs/casket_publish"

# 登録対象拡張子 全ファイルを外部フィルター(estfx)でテキスト化する。
_INDEX_EXTS  = {".txt", ".html", ".htm", ".md", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx", ".bat", ".wsf",
                ".c", ".cpp", ".h", ".cs", ".java", ".go", ".rs", ".rb", ".php",
                ".swift", ".kt", ".scala", ".sh", ".ps1", ".pl", ".lua", ".dart",
                ".ex", ".exs", ".hs", ".clj", ".fs", ".jl", ".r",
                ".sql", ".json", ".yaml", ".yml", ".toml", ".xml",
                ".vb", ".resx", ".rtf",
                ".pdf", ".docx", ".doc", ".xlsx", ".pptx"}
# -fx 外部フィルター。出力はテキストなので T@ 指定
_FILTER_SUFS = ",".join(sorted(_INDEX_EXTS))
_FILTER_CMD  = "T@/usr/local/bin/estfx"

def _find_files(dirpath):
    """コンテナ内 dirPath 配下の全ファイルを再帰取得"""
    r = subprocess.run(["docker", "exec", docker.CONTAINER, "find", dirpath, "-type", "f"],
                       capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l]

def _chain(dir_path, fpath, depth):
    """fpath の所属ディレクトリ chain を dir_path 起点で算出し depth+1 要素にcap"""
    segs = fpath[len(dir_path):].lstrip("/").split("/")[:-1]  # ファイル名を除くdirセグメント
    chain = [dir_path]
    cur = dir_path
    for s in segs:
        cur += "/" + s
        chain.append(cur)
    return tuple(chain[:depth + 1])

def _gather_entry(genre_name, entry):
    """1エントリのgather実行。ディレクトリchain毎に @root/@dep<n> を付与"""
    dir_path = entry["dirPath"]
    root_name = entry["rootName"]
    depth    = int(entry.get("depth", 2))
    regex    = entry.get("regex") or ""
    exregex  = entry.get("exregex") or ""
    casket   = f"/casket/{genre_name}"

    # 全ファイルを再帰収集し chain(深さcap) 毎にグループ化
    groups = {}  # chain(tuple) -> [fpath...]
    total = 0
    for fpath in _find_files(dir_path):
        if regex and not re.search(regex, fpath):
            continue
        if exregex and re.search(exregex, fpath):
            continue
        if os.path.splitext(fpath)[1].lower() not in _INDEX_EXTS:
            continue
        groups.setdefault(_chain(dir_path, fpath, depth), []).append(fpath)
        total += 1

    if not total:
        print(f"  <{root_name}> no files matched")
        return

    print(f"  <{root_name}> {total} files ", end="", flush=True)

    def dot(line):
        # 新規登録(registered)は + 、既登録スキップ(passed)は .
        if ": registered" in line:
            print("+", end="", flush=True)
        elif ": passed" in line:
            print(".", end="", flush=True)

    gid = builder.md5(genre_name)
    for chain, files in groups.items():
        opts = ["-cl", "-xl", "-il", "ja", "-bc", "-lt", "-1", "-lf", "-1",
                "-sd", "-cm", "-cs", "512", "-pc", "UTF-8",
                "-aa", "@genre", gid, "-aa", "@root", builder.md5(chain[0])]
        for i in range(1, len(chain)):
            opts += ["-aa", f"@dep{i}", builder.md5(chain[i])]
        # 全ファイルを estfx でテキスト化 (本文先頭にパス付与、-fx の出力はテキスト=T@)
        docker.estcmd("gather", *opts, "-fx", _FILTER_SUFS, _FILTER_CMD, casket, "-",
                      stdin="\n".join(files) + "\n", check=False, on_line=dot)
    print(" done")

def _doc_paths(casket):
    """casket内の (id, uri, path) 一覧。path は file:// と percent を除去"""
    r = docker.estcmd("list", casket, quiet=True, check=False)
    out = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        did, _, uri = line.partition("\t")
        path = unquote(uri[7:]) if uri.startswith("file://") else uri
        out.append((did, uri, path))
    return out

def _under(path, dirs):
    return any(path == d or path.startswith(d + "/") for d in dirs)

def _purge_ghosts(conf, genre_name):
    """現dirPath配下に属さない旧root由来のdocを除去。rootName変更等でdirPathが
    変わると旧パスのdocが残り続けるのを防ぐ。casketは当該genre基準、MERGEDは
    全genreのdirPath union基準で掃除する(他genreの正規docを保護)"""
    genres = cfg.get_genres(conf)
    casket = f"/casket/{genre_name}"
    g_dirs = [e["dirPath"].rstrip("/") for e in genres[genre_name]]
    all_dirs = [e["dirPath"].rstrip("/") for es in genres.values() for e in es]
    targets = [(casket, [d for d, u, p in _doc_paths(casket) if not _under(p, g_dirs)]),
               (MERGED, [u for d, u, p in _doc_paths(MERGED) if not _under(p, all_dirs)])]
    total = sum(len(x) for _, x in targets)
    if not total:
        return
    print(f"=== purge ghost roots [{genre_name}] ===")
    print(f"  {total} docs ", end="", flush=True)
    for db, exprs in targets:
        for expr in exprs:
            docker.estcmd("out", "-cl", db, expr, check=False, quiet=True)
            print(".", end="", flush=True)
    print(" done")

def cmd_list(conf, args):
    """ジャンル一覧表示"""
    for name in cfg.get_genres(conf):
        print(name)

def cmd_check(conf, args):
    """登録対象ファイルの確認表示"""
    if not args:
        print("usage: est check <genre>", file=sys.stderr); sys.exit(1)
    genre_name = args[0]
    genres = cfg.get_genres(conf)
    if genre_name not in genres:
        print(f"genre [{genre_name}] not found", file=sys.stderr); sys.exit(1)
    for entry in genres[genre_name]:
        print(f"  [{entry['rootName']}]")
        result = docker.estcmd(
            "scandir", "-tf", "-pa", entry["dirPath"],
            check=False
        )

def cmd_gather(conf, args):
    """インデックス登録 merge build publish"""
    if not args:
        print("usage: est gather <genre>", file=sys.stderr); sys.exit(1)
    genre_name = args[0]
    genres = cfg.get_genres(conf)
    if genre_name not in genres:
        print(f"genre [{genre_name}] not found", file=sys.stderr); sys.exit(1)
    t0 = time.time()
    print(f"=== gather [{genre_name}] ===")
    for entry in genres[genre_name]:
        _gather_entry(genre_name, entry)
    elapsed = time.time() - t0
    print(f"done ({elapsed:.1f}s)")
    cmd_merge(conf, [genre_name])
    print(f"=== purge orphan [{genre_name}] ===")
    for entry in genres[genre_name]:
        print(f"  {entry['rootName']} ...", end="", flush=True)
        docker.estcmd("purge", "-cl", MERGED, entry["dirPath"], check=False, quiet=True)
        print(" done")
    _purge_ghosts(conf, genre_name)
    cmd_build(conf, [])
    cmd_publish(conf, [])

def cmd_purge(conf, args):
    """インデックス削除"""
    if not args:
        print("usage: est purge <genre>", file=sys.stderr); sys.exit(1)
    genre_name = args[0]
    print(f"=== purge [{genre_name}] ===")
    casket = f"/casket/{genre_name}"
    result = docker.estcmd("list", casket, quiet=True)
    total = sum(1 for l in result.stdout.splitlines() if l.strip())
    print(f"  {total} files ", end="", flush=True)
    def dot(line):
        if ": deleted" in line:
            print(".", end="", flush=True)
    docker.estcmd("purge", "-cl", "-fc", casket, check=False, on_line=dot)
    print(" done")

def cmd_merge(conf, args):
    """genre毎の casket を casket_merged に統合し最適化"""
    if args:
        # gatherから: 指定genreだけ追加merge (casket_merged は消さない)
        genre_name = args[0]
        casket = f"/casket/{genre_name}"
        if docker.sh("test", "-e", f"{MERGED}/_idx", check=False, quiet=True).returncode != 0:
            docker.estcmd("create", "-xl", MERGED, check=False, quiet=True)
        print(f"=== merge [{genre_name}] ===")
        print(f"  merge ...", end="", flush=True)
        docker.estcmd("merge", MERGED, casket, check=False, quiet=True)
        print(" done")
        return
    # 単体実行: 全genre再ビルド
    print("=== merge ===")
    docker.sh("sh", "-c", f"rm -rf {MERGED}/*", check=False, quiet=True)
    docker.estcmd("create", "-xl", MERGED, check=False, quiet=True)
    for name in cfg.get_genres(conf):
        casket = f"/casket/{name}"
        if docker.sh("test", "-e", f"{casket}/_idx", check=False, quiet=True).returncode != 0:
            print(f"  [{name}] not gathered, skip")
            continue
        print(f"  [{name}] merge ...", end="", flush=True)
        docker.estcmd("merge", MERGED, casket, check=False, quiet=True)
        print(" done")
    print("  optimize ...", end="", flush=True)
    docker.estcmd("optimize", MERGED, check=False, quiet=True)
    print(" done")
    print("  extkeys ...", end="", flush=True)
    docker.estcmd("extkeys",  MERGED, check=False, quiet=True)
    print(" done")

def cmd_publish(conf, args):
    """casket_merged を公開フォルダ(htdocs/casket_publish)へコピー (parts温存)"""
    print("=== publish ===")
    if docker.sh("test", "-e", f"{MERGED}/_idx", check=False, quiet=True).returncode != 0:
        print("casket_merged が空です。先に merge してください", file=sys.stderr); sys.exit(1)
    docker.sh("sh", "-c", f"cp -a {MERGED}/. {PUBLISH}/")
    print(f"  -> {PUBLISH}")
    print("done")

def cmd_build(conf, args):
    """Webメニュー parts を生成し genre を結合 (org build+pack 相当)"""
    print("=== build ===")
    builder.build(conf)
    builder.pack(conf)
    print("done")

def _purge_unregistered_caskets(conf):
    """est.yaml に登録の無い genre の casket を /casket から削除"""
    genres = set(cfg.get_genres(conf))
    r = docker.sh("find", CASKET, "-mindepth", "1", "-maxdepth", "1", "-type", "d",
                  check=False, quiet=True)
    dirs = [os.path.basename(l) for l in r.stdout.splitlines() if l.strip()]
    extra = [d for d in dirs if d not in genres]
    if not extra:
        return
    for d in extra:
        print(f"  rm casket [{d}] ...", end="", flush=True)
        docker.sh("rm", "-rf", f"{CASKET}/{d}", check=False, quiet=True)
        print(" done")

def cmd_optimize(conf, args):
    """casket_merged の最適化"""
    print("=== optimize ===")
    _purge_unregistered_caskets(conf)
    print("  optimize ...", end="", flush=True)
    docker.estcmd("optimize", MERGED, check=False, quiet=True)
    print(" done")
    print("  extkeys ...", end="", flush=True)
    docker.estcmd("extkeys",  MERGED, check=False, quiet=True)
    print(" done")

def cmd_regather(conf, args):
    """purgeしてgather"""
    if not args:
        print("usage: est regather <genre>", file=sys.stderr); sys.exit(1)
    genre_name = args[0]
    genres = cfg.get_genres(conf)
    if genre_name not in genres:
        print(f"genre [{genre_name}] not found", file=sys.stderr); sys.exit(1)
    cmd_purge(conf, args)
    if docker.sh("test", "-e", f"{MERGED}/_idx", check=False, quiet=True).returncode == 0:
        print(f"=== purge merged [{genre_name}] ===") # mergedからもgenreを強制削除
        for entry in genres[genre_name]:
            print(f"  {entry['rootName']} ...", end="", flush=True)
            docker.estcmd("purge", "-cl", "-fc", MERGED, entry["dirPath"], check=False, quiet=True)
            print(" done")
    cmd_gather(conf, args)


