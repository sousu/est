#!/usr/bin/env python3
"""purge: casketから存在しないファイルのエントリを削除"""
import os,sys
from urllib.parse import unquote
from common import load_config,genre_conf,die,log,CASKET,run_estcmd

def uri2path(uri):
    if uri.startswith('file://'):uri=uri[7:]
    return unquote(uri)

def purge(genre,opts=None):
    cfg=load_config()
    gc=genre_conf(cfg,genre)
    if not gc:die(f"genre not found: {genre}")
    casket=os.path.join(CASKET,genre)
    if not os.path.isdir(casket):die(f"casket not found: {casket}")
    entries=[]
    for line in run_estcmd(['list',casket]).splitlines():
        if not line.strip():continue
        eid,_,uri=line.partition('\t')
        entries.append((eid,uri))
    total=len(entries)
    log(f"purge {genre}: {total} entries")
    n=del_n=0
    for eid,uri in entries:
        n+=1
        if n%100==0 or n==total:
            sys.stdout.write('.')
            sys.stdout.flush()
            if n%5000==0:sys.stdout.write(f" {n}\n")
        if not os.path.exists(uri2path(uri)):
            run_estcmd(['out',casket,eid])
            del_n+=1
    sys.stdout.write('\n')
    log(f"purge done: {del_n} purged")

def main(argv):
    if len(argv)<1:die("usage: est purge <genre>")
    purge(argv[0])

if __name__=='__main__':
    main(sys.argv[1:])
