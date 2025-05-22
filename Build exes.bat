@Echo off
title xbdStats to EXE
REM Mode con:cols=70 lines=11
color 4F
setlocal enabledelayedexpansion

set "zip=C:\Program Files\7-Zip\7z.exe"
set "archive_name=XBDStats Server"
set "extra_name1=UDP Client Test"

start /wait C:\Python312\Scripts\cxfreeze.exe "server.py" --target-dir "!archive_name!"
ren "!archive_name!\server.exe" "!archive_name!.exe"
start /wait C:\Python312\Scripts\cxfreeze.exe "!extra_name1!.py" --target-dir "!extra_name1!"

:Start
	del /q "!archive_name!.zip" > NUL
	"!zip!" a "!archive_name!.zip" "!archive_name!" -mx=9 -r -y
	"!zip!" a "!archive_name!.zip" "!extra_name1!" -mx=9 -r -y
	"!zip!" a "!archive_name!.zip" "Client Test Settings.ini" -mx=9 -r -y
	
	(
		echo @Echo off
		echo "!archive_name!\!archive_name!.exe"
	)>"Run !archive_name!.bat"

	"!zip!" a "!archive_name!.zip" "Run !archive_name!.bat" -mx=9 -r -y
	del /q "Run !archive_name!.bat" > NUL
	
	(
		echo @Echo off
		echo start "" "!archive_name!\!archive_name!.exe"
		echo.
		echo if not exist "Client Test Settings.ini" ^(
		echo 	echo ^^[server^^]
		echo 	echo ip=192.168.1.87
		echo 	echo port=1102
		echo ^)^>Client Test Settings.ini
		echo.
		echo start "" "!extra_name1!\!extra_name1!.exe"
	)>"Run !archive_name! + !extra_name1!.bat"

	"!zip!" a "!archive_name!.zip" "Run !archive_name! + !extra_name1!.bat" -mx=9 -r -y
	del /q "Run !archive_name! + !extra_name1!.bat" > NUL

	REM Cleanup
	rmdir /s /q "!archive_name!" > NUL
	rmdir /s /q "!extra_name1!" > NUL