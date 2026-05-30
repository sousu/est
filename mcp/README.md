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

## 移植元(Windows版)との差分
- estcmd呼び出しを `estcmd_utf8.exe` 直叩き → `docker exec` 経由に変更
- LinuxはネイティブUTF-8のため UTF-8マニフェスト埋め込み(setup_utf8.py)は不要
- 検索結果XMLの名前空間を新版 `http://fallabs.com/hyperestraier/xmlns/search` に対応
