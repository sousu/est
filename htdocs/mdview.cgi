#!/usr/bin/env python3
"""Markdownビューア: /files/*.md へのアクセスをlighttpdのrewriteで受け、HTML描画して返す
QUERY_STRINGの f=<target相対パス> を /target 基準で安全解決し、markdownをHTML化する"""
import html,os,re,sys
import xml.etree.ElementTree as etree
from urllib.parse import unquote_plus
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from pygments.formatters import HtmlFormatter

BASE="/target"

# 本文中に直書きされた裸のURL(http/https)を<a>リンク化する拡張
class _BareLink(InlineProcessor):
 def handleMatch(self,m,data):
  url=m.group(1).rstrip(".,;:!?)]}>\"'")  # 末尾の句読点・閉じ括弧等は除外
  el=etree.Element("a");el.set("href",url);el.text=url
  return el,m.start(0),m.start(0)+len(url)
class AutolinkExt(Extension):
 def extendMarkdown(self,md):
  md.inlinePatterns.register(_BareLink(r'(https?://[^\s<>"]+)',md),"barelink",115)

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

def decode(b):
 # ISO-2022-JPは全バイトが7bitでutf-8等もstrict成功し化けるため、ESC(0x1B)有無で先に判定
 # 残りはutf-8→euc-jp→cp932をstrict試行(euc優先でcp932誤判定を抑制) 全滅ならUTF-8で置換
 cands=(["iso-2022-jp"] if b"\x1b" in b else [])+["utf-8-sig","utf-8","euc-jp","cp932"]
 for enc in cands:
  try:return b.decode(enc)
  except UnicodeDecodeError:pass
 return b.decode("utf-8",errors="replace")

_URL=re.compile(r'https?://[^\s<>"]+')
def txt2html(s):
 # txtはmarkdown解釈せず、エスケープしたうえで裸URLのみ<a>化(改行・空白は<pre>で保持)
 out=[];pos=0
 for m in _URL.finditer(s):
  out.append(html.escape(s[pos:m.start()]))
  url=m.group(0).rstrip(".,;:!?)]}>\"'");tail=m.group(0)[len(url):]
  out.append(f'<a target="_blank" rel="noopener" href="{html.escape(url,True)}">{html.escape(url)}</a>{html.escape(tail)}')
  pos=m.end()
 out.append(html.escape(s[pos:]))
 return "".join(out)

with open(path,"rb") as fp:text=decode(fp.read())
if path.lower().endswith(".txt"):
 body=f'<pre class="txt">{txt2html(text)}</pre>'
else:
 body=markdown.markdown(text,extensions=["fenced_code","tables","codehilite","toc","sane_lists",AutolinkExt()],
  extension_configs={"codehilite":{"guess_lang":False}})
 # 外部URLリンク(http/https)のみ別タブで開く(TOC等の#アンカーは対象外)
 body=re.sub(r'<a href="(https?://)',r'<a target="_blank" rel="noopener" href="\1',body)
title=html.escape(os.path.basename(path))
css=HtmlFormatter().get_style_defs(".codehilite")

# ここから下が画面のスタイル
STYLE="""
body{
 font-size:14px;
 font-family:-apple-system,"Segoe UI","Helvetica Neue","Hiragino Sans","Noto Sans JP",sans-serif;
 line-height:1.7;
 color:#1f2328;
 max-width:900px;
 margin:0 auto;
 padding:24px 32px;
 word-wrap:break-word;
}
h1,h2{
 border-bottom:1px solid #d8dee4;
 padding-bottom:.3em;
}
h1,h2,h3,h4{
 margin-top:1.5em;
 margin-bottom:.6em;
 font-weight:600;
 line-height:1.25;
}
a{
 color:#0969da;
 text-decoration:none;
}
a:hover{
 text-decoration:underline;
}
code{
 background:#eff1f3;
 padding:.2em .4em;
 border-radius:6px;
 font-size:85%;
 font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
}
pre{
 background:#f6f8fa;
 padding:16px;
 border-radius:6px;
 overflow:auto;
 line-height:1.45;
}
pre code{
 background:none;
 padding:0;
 font-size:100%;
}
pre.txt{
 background:none;
 padding:0;
 font-family:inherit;
 font-size:inherit;
 line-height:inherit;
 white-space:pre-wrap;
 word-wrap:break-word;
}
blockquote{
 margin:0;
 padding:0 1em;
 color:#59636e;
 border-left:.25em solid #d1d9e0;
}
table{
 border-collapse:collapse;
 display:block;
 overflow:auto;
}
th,td{
 border:1px solid #d1d9e0;
 padding:6px 13px;
}
tr:nth-child(2n){
 background:#f6f8fa;
}
img{
 max-width:100%;
}
hr{
 border:none;
 border-top:1px solid #d8dee4;
 margin:24px 0;
}
"""

out=f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
{STYLE}
{css}
</style></head><body>{body}</body></html>"""
sys.stdout.write("Content-Type: text/html;charset=UTF-8\r\n\r\n")
sys.stdout.write(out)
