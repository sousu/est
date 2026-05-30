"""genres.yaml を読み込みジャンル/設定を提供する"""
import os
import yaml

DEFAULT_CONF = os.path.join(os.path.dirname(__file__), "../est.yaml")

def load(path=None):
    path = path or os.environ.get("EST_CONF", DEFAULT_CONF)
    with open(os.path.abspath(path)) as f:
        return yaml.safe_load(f)

def get_genres(conf):
    return conf.get("genres", {})

def get_config(conf):
    return conf.get("config", {})
