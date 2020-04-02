
## est

HyperEstraier のラッパーコマンド及び Webビュー自動生成ツール

### 導入

 - HyperEstraierのパッケージの構成にまるごとコピー
 - ``estseek.c``に``tool/estseek.c.diff``でパッチ当て
 - apacheを設定
 - ジャンクション設定``mklink /J C:\path\to\htdocs\est C:\path\to\develop\est``

 - ``est_tmpl.xls``を``est.xls``にコピーしてディレクトリの設定／インデクスの登録
 - ``estseek_tmpl.conf``を``estseek.conf``に変更して各種設定
 - ``script/make_index.bat``を実行してインデクス初期作成

### コマンド

インデクス名確認

    cscript ./estjob.wsf list

インデクス作成

    cscript ./estjob.wsf gather INDEX_NAME

