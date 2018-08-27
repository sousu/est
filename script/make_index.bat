
rem インデクス初期化スクリプト

set EST=%~p0\..\
pushd %EST%

estcmd create -xh casket_work
estcmd create -xh casket_publish

