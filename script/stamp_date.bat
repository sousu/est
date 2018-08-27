
set EST=%~p0\..\
set LOG_NAME=g
pushd %EST%

echo ------------------------------------------------------- >> %EST%\log\%LOG_NAME%.txt
echo ###DATE################################################ >> %EST%\log\%LOG_NAME%.txt
echo %date% %time% >> %EST%\log\%LOG_NAME%.txt
echo ####################################################### >> %EST%\log\%LOG_NAME%.txt
echo ------------------------------------------------------- >> %EST%\log\%LOG_NAME%.txt


