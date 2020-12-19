
## est

HyperEstraier のラッパーコマンド及び Webビュー自動生成ツール

### 導入

 + HyperEstraierのパッケージ構成に当該ツールの構成を丸ごと上書き
 + ソースから``estseek.c``に``tool/estseek.c.diff``でパッチ当てし``estseek.cgi``は再ビルド
 + ウェブサーバを設定
 + ウェブサーバにジャンクション設定``mklink /J C:\path\to\htdocs\est C:\path\to\est``
 + ``est_tmpl.xls``を``est.xls``にコピーしてディレクトリの設定／インデクスの登録
 + ``estseek_tmpl.conf``を``estseek.conf``に変更して各種設定
 + ``script/make_index.bat``を実行してインデクス初期作成

### コマンド

インデクス名確認

    cscript ./estjob.wsf list

インデクス作成

    cscript ./estjob.wsf gather INDEX_NAME

