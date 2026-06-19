#!/usr/bin/env python3
"""ディレクトリ一覧ビューア: /files/<dir>/ へのアクセスをlighttpdのrewriteで受け、
配下のファイル・サブディレクトリを安全にリスト表示する
QUERY_STRINGの d=<target相対パス> を /target 基準で安全解決する"""
import html,os,sys,time
from urllib.parse import unquote_plus,quote

BASE="/target"

def err(status,msg):
 sys.stdout.write(f"Status: {status}\r\nContent-Type: text/plain;charset=UTF-8\r\n\r\n{msg}\n")
 sys.exit()

q=os.environ.get("QUERY_STRING","")
d=""
for kv in q.split("&"):
 if kv.startswith("d="):d=unquote_plus(kv[2:])
# /target基準で正規化し、範囲外(../等)・非ディレクトリを拒否
path=os.path.realpath(os.path.join(BASE,d.lstrip("/")))
if not(path==BASE or path.startswith(BASE+os.sep)):err("403 Forbidden","out of range")
if not os.path.isdir(path):err("404 Not Found","not a directory")
rel="" if path==BASE else os.path.relpath(path,BASE)  # ルートは空文字

def url(p):  # /target相対パスをブラウザアクセス用URLへ(/が崩れないようsafe指定)
 return "/files/"+quote(p,safe="/")

# 配下を収集。隠しファイルは除外、シンボリックリンクで/target外へ出るものも除外
dirs=[];files=[]
for name in sorted(os.listdir(path),key=str.lower):
 if name.startswith("."):continue
 full=os.path.join(path,name)
 real=os.path.realpath(full)
 if not(real==BASE or real.startswith(BASE+os.sep)):continue
 try:st=os.stat(full)
 except OSError:continue
 (dirs if os.path.isdir(full) else files).append((name,st))

def fsize(n):
 for u in("B","KB","MB","GB"):
  if n<1024:return f"{n:.0f}{u}" if u=="B" else f"{n:.1f}{u}"
  n/=1024
 return f"{n:.1f}TB"

# パンくず(各階層をリンク化)
crumbs=['<a href="/files/">target</a>']
acc=""
for part in([] if rel=="" else rel.split("/")):
 acc=(acc+"/"+part) if acc else part
 crumbs.append(f'<a href="{html.escape(url(acc),True)}/">{html.escape(part)}</a>')
nav=" / ".join(crumbs)

rows=[]
# 親ディレクトリへ
if rel!="":
 parent=os.path.dirname(rel)
 phref=url(parent)+"/" if parent else "/files/"
 rows.append(f'<tr class="up"><td class="ic">⬆</td><td><a href="{html.escape(phref,True)}">..</a></td><td></td><td></td></tr>')
for name,st in dirs:
 p=(rel+"/"+name) if rel else name
 rows.append(f'<tr><td class="ic">📁</td><td><a class="d" href="{html.escape(url(p)+"/",True)}">{html.escape(name)}/</a></td>'
  f'<td class="sz"></td><td class="dt">{time.strftime("%Y-%m-%d %H:%M",time.localtime(st.st_mtime))}</td></tr>')
for name,st in files:
 p=(rel+"/"+name) if rel else name
 rows.append(f'<tr><td class="ic">📄</td><td><a href="{html.escape(url(p),True)}">{html.escape(name)}</a></td>'
  f'<td class="sz">{fsize(st.st_size)}</td><td class="dt">{time.strftime("%Y-%m-%d %H:%M",time.localtime(st.st_mtime))}</td></tr>')
if not rows:rows.append('<tr><td></td><td class="empty">(空)</td><td></td><td></td></tr>')

title=html.escape(os.path.basename(rel) if rel else "target")
STYLE="""
body{font-size:14px;font-family:-apple-system,"Segoe UI","Helvetica Neue","Hiragino Sans","Noto Sans JP",sans-serif;
 line-height:1.6;color:#1f2328;max-width:900px;margin:0 auto;padding:24px 32px;}
h1{font-size:18px;font-weight:600;margin:0 0 4px;}
.crumb{font-size:13px;color:#59636e;margin-bottom:16px;word-break:break-all;}
.crumb a{color:#0969da;text-decoration:none;}
.crumb a:hover{text-decoration:underline;}
table{border-collapse:collapse;width:100%;}
td{border-bottom:1px solid #eaecef;padding:6px 10px;vertical-align:top;}
td.ic{width:1.4em;text-align:center;color:#59636e;}
a{color:#0969da;text-decoration:none;word-break:break-all;}
a:hover{text-decoration:underline;}
a.d{font-weight:600;}
.sz{width:7em;text-align:right;color:#59636e;white-space:nowrap;}
.dt{width:10em;color:#59636e;white-space:nowrap;font-variant-numeric:tabular-nums;}
tr.up a{color:#59636e;}
.empty{color:#8c959f;}
@media(max-width:600px){
 body{padding:16px 12px;}
 td{padding:7px 4px;}
 td.ic{width:1.2em;}
 .dt{display:none;}
 .sz{width:auto;font-size:12px;padding-left:8px;}
}
"""
out=f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{STYLE}</style></head><body>
<h1>{title}</h1>
<div class="crumb">{nav}</div>
<table>{''.join(rows)}</table>
</body></html>"""
sys.stdout.write("Content-Type: text/html;charset=UTF-8\r\nX-Content-Type-Options: nosniff\r\n"
 "Content-Security-Policy: default-src 'none';style-src 'unsafe-inline'\r\n\r\n")
sys.stdout.write(out)
