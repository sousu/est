
rem �^�X�N�o�^�p���s�X�N���v�g

set EST=%~p0\..\
pushd %EST%

for %%i in (TOPS�J��,FACE�J��,ADEX�J��,SDECC�Ɩ�) do (

cscript //nologo estjob.wsf gather %%i >> %EST%\log\g.txt

)


