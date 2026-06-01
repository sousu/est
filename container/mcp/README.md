# MCP for Hyper Estraier (Linux/Docker版)

Hyper Estraier の全文検索をLLMから使うためのMCPサーバ。
estcmd はホスト直叩きではなく `docker exec -i est estcmd ...` 経由で呼び出す。

## 構成
- `main.py` — FastMCPサーバ本体(`search`/`detail`/`list_genres`/`list_roots`)

## 前提
- estコンテナ(`container_name: est`)が起動済み(`docker compose up -d`)
- 公開indexがコンテナ内 `/htdocs/casket_publish`、メニュー用 `parts` が
  ホスト `../htdocs/casket_publish/parts` に存在(`est publish` 後の状態)

## 起動
```
uv run python main.py
```
