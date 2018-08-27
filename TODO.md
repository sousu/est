
### TODO&MEMO

コマンド

 - 「&」のエスケープ処理
 - TMP出力の成るべくの未使用化
 - Depth設定が想定より1段深い点
 - Indexのパス不正時処理
 - RootをIndexに書き換え
 - optimize時にpartsを整理する処理を追加/pack内
 
Webビュー

 - Genre毎に最終更新時間を表示
 - Genreの属性指定化
 - 更新日時変換にてIE8で時分に10を含む場合のNaN
 - Regex設定時のDir下階層だけにマッチした場合の上位階層の抜け発生の対応

### 要素整理

**Genres**

 - 最も上位のカテゴリ，Rootを1種以上持つ／設定ファイルのシート名に対応
 - 構築時はID付きaタグを集計したgenresを作る
 - Genre内各Rootをli要素で並べたentry_rootsを作る
 - Genre内Dirの番号とIDの対応表を一覧するids(Json)を作る

**Root(Index)**

 - Genre配下のサブカテゴリ，est設定ファイルの各行に対応

**Dir**

 - Root配下の各ディレクトリ，インデクス登録時の処理単位

