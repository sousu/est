
rem タスク登録用実行スクリプト

set EST=%~p0\..\
pushd %EST%

cscript //nologo estjob.wsf optimize

