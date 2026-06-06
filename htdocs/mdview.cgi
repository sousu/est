#!/usr/bin/env python3
"""Markdownビューア: /files/*.md へのアクセスをlighttpdのrewriteで受け、HTML描画して返す。
QUERY_STRINGの f=<target相対パス> を /target 基準で安全解決し、markdownをHTML化する。"""
import html,os,sys
from urllib.parse import unquote_plus
import markdown
from pygments.formatters import HtmlFormatter

BASE="/target"

def err(status,msg):
 sys.stdout.write(f"Status: {status}\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\n{msg}\n")
 sys.exit()

q=os.environ.get("QUERY_STRING","")
f=""
for kv in q.split("&"):
 if kv.startswith("f="):f=unquote_plus(kv[2:])
if not f:err("400 Bad Request","missing f")
path=os.path.realpath(os.path.join(BASE,f.lstrip("/")))
if not(path==BASE or path.startswith(BASE+os.sep)):err("403 Forbidden","out of range")
if not path.lower().endswith(".md") or not os.path.isfile(path):err("404 Not Found","not a markdown file")

def decode(b):
 # ISO-2022-JPは全バイトが7bitでutf-8等もstrict成功し化けるため、ESC(0x1B)有無で先に判定。
 # 残りはutf-8→euc-jp→cp932をstrict試行(euc優先でcp932誤判定を抑制)。全滅ならUTF-8で置換。
 cands=(["iso-2022-jp"] if b"\x1b" in b else [])+["utf-8-sig","utf-8","euc-jp","cp932"]
 for enc in cands:
  try:return b.decode(enc)
  except UnicodeDecodeError:pass
 return b.decode("utf-8",errors="replace")

with open(path,"rb") as fp:text=decode(fp.read())
body=markdown.markdown(text,extensions=["fenced_code","tables","codehilite","toc","sane_lists"],
 extension_configs={"codehilite":{"guess_lang":False}})
title=html.escape(os.path.basename(path))
css=HtmlFormatter().get_style_defs(".codehilite")
out=f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
body{{font-size:14px;font-family:-apple-system,"Segoe UI","Helvetica Neue","Hiragino Sans","Noto Sans JP",sans-serif;
line-height:1.7;color:#1f2328;max-width:900px;margin:0 auto;padding:24px 32px;word-wrap:break-word}}
h1,h2{{border-bottom:1px solid #d8dee4;padding-bottom:.3em}}
h1,h2,h3,h4{{margin-top:1.5em;margin-bottom:.6em;font-weight:600;line-height:1.25}}
a{{color:#0969da;text-decoration:none}}a:hover{{text-decoration:underline}}
code{{background:#eff1f3;padding:.2em .4em;border-radius:6px;font-size:85%;
font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace}}
pre{{background:#f6f8fa;padding:16px;border-radius:6px;overflow:auto;line-height:1.45}}
pre code{{background:none;padding:0;font-size:100%}}
blockquote{{margin:0;padding:0 1em;color:#59636e;border-left:.25em solid #d1d9e0}}
table{{border-collapse:collapse;display:block;overflow:auto}}
th,td{{border:1px solid #d1d9e0;padding:6px 13px}}tr:nth-child(2n){{background:#f6f8fa}}
img{{max-width:100%}}hr{{border:none;border-top:1px solid #d8dee4;margin:24px 0}}
{css}
</style></head><body>{body}</body></html>"""
sys.stdout.write("Content-Type: text/html;charset=UTF-8\r\n\r\n")
sys.stdout.write(out)
