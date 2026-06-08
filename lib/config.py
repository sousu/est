"""genres.yaml を読み込みジャンル/設定を提供する"""
import os
import yaml

DEFAULT_CONF = os.path.join(os.path.dirname(__file__), "../est.yaml")

def load(path=None):
    path = path or os.environ.get("EST_CONF", DEFAULT_CONF)
    with open(os.path.abspath(path)) as f:
        return yaml.safe_load(f)

def get_genres(conf):
    # dirPath は絶対パスに正規化(相対指定でもURI由来パスとghost/orphan purgeの判定を一致させる)
    genres = conf.get("genres", {})
    for entries in genres.values():
        for e in entries:
            d = (e.get("dirPath") or "").rstrip("/")
            if d and not d.startswith("/"):
                d = "/" + d
            e["dirPath"] = d
    return genres

def get_config(conf):
    return conf.get("config", {})
