from __future__ import annotations
import json, subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from fastmcp import FastMCP

CONTAINER = "est"
CASKET = "/htdocs/casket_publish"  # コンテナ内パス
PARTS = Path(__file__).resolve().parent.parent / "htdocs" / "casket_publish" / "parts"
MAX_HITS = 100
NS = {"e": "http://fallabs.com/hyperestraier/xmlns/search"}

mcp = FastMCP("est")

def _estcmd(*args: str) -> str:
    cmd = ["docker", "exec", "-i", CONTAINER, "estcmd", *args]
    p = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    return p.stdout

def _read(name: str) -> str:
    return (PARTS / name).read_text(encoding="utf-8")

def _genres() -> list[dict]:
    soup = BeautifulSoup(_read("genre"), "html.parser")
    return [{"id": a["id"], "name": a.get_text(strip=True)} for a in soup.select("a.genre_link")]

def _genre_id(name: str) -> str:
    for g in _genres():
        if g["name"] == name: return g["id"]
    raise ValueError(f"genre not found: {name}")

def _roots(gid: str) -> list[dict]:
    soup = BeautifulSoup(_read(f"{gid}_entry_roots"), "html.parser")
    ids = json.loads(_read(f"{gid}_ids.json"))
    out = []
    for li in soup.select("li"):
        inp, lbl = li.select_one("input.dir"), li.select_one("label")
        if inp and lbl:
            did = inp["id"]
            out.append({"id": did, "name": lbl.get_text(strip=True), "hash": ids.get(did, "")})
    return out

def _snippet(el) -> str:
    parts = [el.text or ""]
    for c in el:
        tag = c.tag.rsplit("}", 1)[-1]
        parts.append(" … " if tag == "delimiter" else (c.text or ""))
        parts.append(c.tail or "")
    return " ".join("".join(parts).split())

def _est_search(phrase: str | None, attrs: list[str], max_n: int = MAX_HITS) -> tuple[int, list[dict]]:
    cmd = ["search", "-vx", "-sn", "900", "200", "200", "-max", str(max_n)]
    if phrase: cmd += ["-sf"]
    for a in attrs: cmd += ["-attr", a]
    cmd += [CASKET, phrase or "[UVSET]"]
    root = ET.fromstring(_estcmd(*cmd))
    hit_el = root.find("e:meta/e:hit", NS)
    hits = int(hit_el.get("number", "0")) if hit_el is not None else 0
    out = []
    for d in root.findall("e:document", NS):
        attr = {a.get("name"): a.get("value") for a in d.findall("e:attribute", NS)}
        sn = d.find("e:snippet", NS)
        out.append({
            "title": attr.get("@title") or attr.get("_lfile") or "",
            "uri": attr.get("_lreal") or d.get("uri", ""),
            "snippet": _snippet(sn) if sn is not None else "",
            "size": int(attr["@size"]) if attr.get("@size", "").isdigit() else None,
            "id": int(d.get("id")) if d.get("id") else None,
        })
    return hits, out

def _query_attrs(phrase, genre, roots) -> list[str]:
    if not phrase and not genre and not roots:
        raise ValueError("phrase / genre / roots のいずれか1つ以上を指定してください")
    attrs: list[str] = []
    hashes: set[str] = set()
    if genre:
        gid = _genre_id(genre)
        attrs.append(f"@genre STREQ {gid}")
        if roots:
            by_name = {r["name"]: r["hash"] for r in _roots(gid)}
            missing = [n for n in roots if n not in by_name]
            if missing: raise ValueError(f"roots not found: {missing}")
            hashes = {by_name[n] for n in roots}
    elif roots:
        names, found = set(roots), set()
        for g in _genres():
            for r in _roots(g["id"]):
                if r["name"] in names:
                    hashes.add(r["hash"]); found.add(r["name"])
        missing = names - found
        if missing: raise ValueError(f"roots not found: {sorted(missing)}")
    if hashes: attrs.append("@root STROREQ " + " ".join(sorted(hashes)))
    return attrs


@mcp.tool()
def search(phrase: str | None = None, genre: str | None = None, roots: list[str] | None = None) -> dict:
    """Hyper Estraierでキーワード検索。{"hits": 総ヒット数, "results": 最大100件} を返す。
    並び順: phrase指定時はスコア(関連度)降順、phrase未指定時は登録順。
    hits が results の件数より大きい場合は絞り込み(genre/roots/phrase の追加)を検討。

      phrase/genre/roots のいずれか1つ以上が必須。
       - phrase指定時は全文検索(複数プロジェクトをまたぐ全文検索向け)
       - genre指定時はジャンル全体を対象(特定ジャンルの複数プロジェクトの検索向け)
       - roots指定時は @root 一致のみ(プロジェクト内の全ファイルを取得)
    """
    attrs = _query_attrs(phrase, genre, roots)
    hits, res = _est_search(phrase, attrs)
    # -attr は post-filter のため通常呼び出しの hit は -max の窓内マッチ数しか映らない。
    # 属性指定時のみ -max 0 (meta のみ出力) で真の総数を取り直す。
    if attrs: hits, _ = _est_search(phrase, attrs, 0)
    return {"hits": hits, "results": res}

@mcp.tool()
def list_genres() -> list[str]:
    """利用可能なジャンル一覧を返す。確認出来たジャンル名により検索可能"""
    return [g["name"] for g in _genres()]

@mcp.tool()
def list_roots(genre: str) -> list[str]:
    """指定ジャンル配下のトップレベルのルート(フォルダ)一覧を返す。確認出来たルート名により検索可能"""
    return [r["name"] for r in _roots(_genre_id(genre))]

@mcp.tool()
def detail(id: int) -> str:
    """Hyper Estraierの文書ID(detail)を指定し、本文を返す。"""
    out = _estcmd("get", CASKET, str(id))
    parts = out.split("\n\n", 1)
    return (parts[1] if len(parts) == 2 else out).strip()

if __name__ == "__main__":
    mcp.run(transport="http",host="0.0.0.0",port=5006)
