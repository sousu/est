"""Web メニュー(parts)生成 — org の builder.js + packer.js 相当
ディレクトリ階層からチェックボックス付きメニュー parts を生成する。
id体系: genre id = md5(genre名), dir id = md5(コンテナ内dirパス)。"""
import hashlib
import os
import re
import subprocess
import time
from . import config as cfg
from . import docker

PARTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../htdocs/casket_publish/parts"))

def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def _matcher(white, black):
    w = re.compile(white) if white else None
    b = re.compile(black) if black else None
    def m(path):
        if w and not w.search(path): return False
        if b and b.search(path): return False
        return True
    return m

def _list_dirs(dirpath, depth):
    """コンテナ内 dirPath 配下のディレクトリを find で取得 (node depth 0..depth)"""
    r = subprocess.run(
        ["docker", "exec", docker.CONTAINER, "find", dirpath,
         "-mindepth", "1", "-maxdepth", str(depth + 1), "-type", "d"],
        capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l]

def _walk(dirpath, e_depth):
    """FileDiver相当の先行順(pre-order)で (name,path,depth,has_child) を返す"""
    dirs = _list_dirs(dirpath, e_depth)
    children = {}
    for p in dirs:
        children.setdefault(p.rsplit("/", 1)[0], []).append(p)
    for k in children:
        children[k].sort()
    out = []
    def rec(parent, depth):
        for p in children.get(parent, []):
            name = p.rsplit("/", 1)[1]
            out.append((name, p, depth, bool(children.get(p))))
            if e_depth >= depth + 1:
                rec(p, depth + 1)
    rec(dirpath, 0)
    return out

class _Build:
    def __init__(self):
        self.cnt = 1
        self.root_cnt = 1
        self.root_html = ""
        self.json = "{ \n"

    def _li_inner(self, name, id_val):
        d = "d%d" % self.cnt
        inner = ('<label for="%s" class="dir_check">'
                 '<input type="checkbox" name="%s" id="%s" class="dir" />%s</label>'
                 % (d, d, d, name))
        self.json += '"%s" : "%s",\n' % (d, id_val)
        self.cnt += 1
        return inner

    def root_li(self, name, path):
        self.root_cnt = self.cnt
        self.root_html += (
            "<li>\n " + self._li_inner(name, md5(path)) + "\n "
            + '<span id="root%d" class="pop_button quickmenu_pop normal">&nbsp;</span>\n '
            % self.root_cnt + "</li>\n")

    def _close(self, num, depth):
        s = ""
        for i in range(num):
            s += " " * (depth - i) + "</ul></li>\n"
        return s

    def sub_menu(self, nodes, e_depth, match):
        html = '<ul class="quickmenu-data" stlye="display:none">\n'
        pre = 0
        for name, path, depth, has_child in nodes:
            if not match(path):
                continue
            diff = depth - pre
            if diff == 1:
                html += "<ul>\n"
            elif diff != 0:
                html += self._close(pre - depth, pre)
            html += " " * (depth + 1) + "<li>" + self._li_inner(name, md5(path))
            if (not has_child) or (depth == e_depth):
                html += "</li>\n"
            pre = depth
        html += self._close(pre, pre)
        html += "</ul>\n"
        return html

def _write(name, content):
    with open(os.path.join(PARTS, name), "w", encoding="utf-8") as f:
        f.write(content)

def _clear_parts():
    for fn in os.listdir(PARTS):
        fp = os.path.join(PARTS, fn)
        if os.path.isfile(fp):
            os.remove(fp)

def build(conf):
    """全genreのメニュー parts を生成"""
    _clear_parts()
    ts = time.strftime("%Y/%m/%d %H:%M")
    for gname, entries in cfg.get_genres(conf).items():
        gid = md5(gname)
        b = _Build()
        for e in entries:
            match = _matcher(e.get("regex"), e.get("exregex"))
            e_depth = int(e.get("depth", 2))
            b.root_li(e["indexName"], e["dirPath"])
            root_cnt = b.root_cnt
            nodes = _walk(e["dirPath"], e_depth)
            _write("%s_root%d" % (gid, root_cnt), b.sub_menu(nodes, e_depth, match))
        _write("%s_entry_roots" % gid, b.root_html)
        b.json += '"end" : "end"\n}'
        _write("%s_ids.json" % gid, b.json)
        _write("genre_%s" % gid,
               '<a href="estseek.cgi" id="%s" class="genre_link">%s</a>\n' % (gid, gname))
        _write("ts_%s.json" % gid, '{ "ts": "%s" }' % ts)

def pack(conf):
    """各genreの genre_<id> を結合して genre ファイルへ"""
    g = ""
    for gname in cfg.get_genres(conf):
        p = os.path.join(PARTS, "genre_%s" % md5(gname))
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                g += f.read() + "\n"
    _write("genre", g)
