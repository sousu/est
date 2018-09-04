
## est

HyperEstraier のラッパーコマンド及び Webビュー

### 導入

 - HyperEstraierのパッケージの構成にまるごとコピー
 - ジャンクション設定

        mklink /J C:\path\to\htdocs\est C:\path\to\develop\est

- Apacheを設定
 - ``estseek.c``にパッチ当て
 - ``est_tmpl.xls``を``est.xls``にコピーしてディレクトリの設定／インデクスの登録
 - ``estseek_tmpl.conf``を``estseek.conf``に変更して各種設定
 - ``script/make_index.bat``を実行してインデクスを初期作成
 - インデクス作成

        cscript ./estjob.wsf gather INDEX_NAME


<!-- vim: set ft=markdown syntax=blogsyntax: -->
