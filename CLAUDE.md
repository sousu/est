
## プロジェクト内容

Windows環境のHyperEstraierのラッパースクリプトのestをLinux環境に移植するプロジェクト
- 移植元のプロジェクトは`_org`配下

方針
- 単純な移植ではなく、元プロジェクトから以下の機能を移植
 - `./_org/estjob.wsf`のコマンドラッパー周り、`./_org/est.xls`やgenre・root等の登録機能
 - `./_org/estseek.*`や`./_org/res`のWeb表示周り
- estcmdはDockerに構築する

開発方法
- ラッパーコマンドにはPythonを使う

## 各フォルダ・ファイルの役割

estcmdによるインデクス関係
- `casket`: genre毎にgather等されるcasketの作業・保存場所
- `casket_merged`: genre毎に作業された後にmergeしたり、全体でoptimize等するための収集・作業場所
- `htdocs/casket_publish`: `casket_merged`で正常作業完了後に丸ごとコピーを行う公開用の保存場所。またWebでメニューを表示する為のpartsフォルダを含む

HyperEstraier及びWeb表示の実行環境関係
- `container`: HyperEstraierのコンパイル後コマンド群及びWeb配信用のlighttpdを備えたコンテナ
- `docker-compose.yml`: 上記コンテナの環境設定及び実行設定
- `htdocs`: lighttpdの公開フォルダとしてマウントされるフォルダ estseek.cgi及びその関係設定・テンプレート・Web表示用ライブラリ等を保管
- `target`: 登録対象のファイルを置き、lighttpdからもマウントされる

ラッパーコマンド関係
- `est`: 移植元のestjob.wsfに相当するラッパーコマンドメイン
- `est.yaml`: 移植元のest.xlsに相当する一括設定ファイル 
- `lib`: estが呼びだす各コマンド等のライブラリ群

mcp関係
- `_mcp`: 移植元mcpサーバ
- `container/mcp`: 移植先

## その他共通注意事項

スクリプトの書き方
- 改行や引数間のスペースは必要最小限にしてコンパクトかつシンプルな見た目にすること

プロジェクトのバックアップ
- 指示する際にバックアップを実行する。作業途中で実行した方がよいタイミングがあれば提案すること
- バックアップはルートフォルダの `_backup` に日付だけのファイル名でzipで取る。日付が同じ場合は上書きして良い
- `_backup`や`_org`等アンダースコアから始まるフォルダ、`casket` `casket_merged` `htdocs/casket_publish` `target`はバックアップに含めないこと

その他の注意点
- どの階層においても`_old`フォルダ内のファイルは気にしないこと

