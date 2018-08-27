
rem タスク登録用実行スクリプト

set EST=%~p0\..\
pushd %EST%

for %%i in (TOPS開発,FACE開発,ADEX開発,SDECC業務) do (

cscript //nologo estjob.wsf gather %%i >> %EST%\log\g.txt

)


