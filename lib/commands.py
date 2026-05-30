"""est サブコマンド実装"""
import os
import re
import subprocess
import sys
import time
from . import config as cfg
from . import docker
from . import builder

# 全genreをmergeする作業db (org の casket_work 相当) と公開先
MERGED  = "/casket_merged"
PUBLISH = "/htdocs/casket_publish"

# -ft (強制テキスト読み込み) で処理する拡張子
_TEXT_EXTS   = {".txt", ".html", ".htm", ".md", ".csv", ".py", ".js", ".ts", ".tsx", ".jsx", ".bat", ".wsf",
                ".c", ".cpp", ".h", ".cs", ".java", ".go", ".rs", ".rb", ".php",
                ".swift", ".kt", ".scala", ".sh", ".ps1", ".pl", ".lua", ".dart",
                ".ex", ".exs", ".hs", ".clj", ".fs", ".jl", ".r",
                ".sql", ".json", ".yaml", ".yml", ".toml", ".xml",
                ".vb", ".resx", ".rtf"}
# -fx 外部フィルター(estfx)でテキスト化する拡張子。出力はテキストなので T@ 指定
_FILTER_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".rtf"}
_FILTER_SUFS = ",".join(sorted(_FILTER_EXTS))
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
    idx_name = entry["indexName"]
    depth    = int(entry.get("depth", 2))
    regex    = entry.get("regex") or ""
    exregex  = entry.get("exregex") or ""
    casket   = f"/casket/{genre_name}"

    # 全ファイルを再帰収集し chain(深さcap) 毎にグループ化、拡張子別に分類
    groups = {}  # chain(tuple) -> {kind: [...]}
    total = 0
    for fpath in _find_files(dir_path):
        if regex and not re.search(regex, fpath):
            continue
        if exregex and re.search(exregex, fpath):
            continue
        ext = os.path.splitext(fpath)[1].lower()
        if ext in _TEXT_EXTS:      kind = "text"
        elif ext in _FILTER_EXTS:  kind = "filter"
        else:                      continue
        g = groups.setdefault(_chain(dir_path, fpath, depth), {})
        g.setdefault(kind, []).append(fpath)
        total += 1

    if not total:
        print(f"  <{idx_name}> no files matched")
        return

    print(f"  <{idx_name}> {total} files ", end="", flush=True)

    def dot(line):
        # 新規登録(registered)・既登録スキップ(passed)とも1ファイル1ドット
        if ": registered" in line or ": passed" in line:
            print(".", end="", flush=True)

    gid = builder.md5(genre_name)
    for chain, files in groups.items():
        opts = ["-cl", "-xl", "-il", "ja", "-bc", "-lt", "-1", "-lf", "-1",
                "-sd", "-cm", "-cs", "512", "-pc", "UTF-8",
                "-aa", "@genre", gid, "-aa", "@root", builder.md5(chain[0])]
        for i in range(1, len(chain)):
            opts += ["-aa", f"@dep{i}", builder.md5(chain[i])]
        if files.get("text"):
            docker.estcmd("gather", *opts, "-ft", casket, "-",
                          stdin="\n".join(files["text"]) + "\n", check=False, on_line=dot)
        # office文書/PDF等は estfx でテキスト化 (-fx の出力はテキスト=T@)
        if files.get("filter"):
            docker.estcmd("gather", *opts, "-fx", _FILTER_SUFS, _FILTER_CMD, casket, "-",
                          stdin="\n".join(files["filter"]) + "\n", check=False, on_line=dot)
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
        print(f"  [{entry['indexName']}]")
        result = docker.estcmd(
            "scandir", "-tf", "-pa", entry["dirPath"],
            check=False
        )

def cmd_gather(conf, args):
    """インデックス登録 → merge → build → publish"""
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
        print(f"  {entry['indexName']} ...", end="", flush=True)
        docker.estcmd("purge", "-cl", MERGED, entry["dirPath"], check=False, quiet=True)
        print(" done")
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

def cmd_optimize(conf, args):
    """casket_merged の最適化"""
    print("=== optimize ===")
    print("  ...", end="", flush=True)
    docker.estcmd("optimize", MERGED, check=False, quiet=True)
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
        print(f"=== purge merged [{genre_name}] ===")
        for entry in genres[genre_name]:
            print(f"  {entry['indexName']} ...", end="", flush=True)
            docker.estcmd("purge", "-cl", "-fc", MERGED, entry["dirPath"], check=False, quiet=True)
            print(" done")
    cmd_gather(conf, args)


