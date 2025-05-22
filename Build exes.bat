@Echo off
title xbdStats to EXE
Mode con:cols=70 lines=11
Color 0B
setlocal enabledelayedexpansion

set "zip=C:\Program Files\7-Zip\7z.exe"
set "archive_name=XBDStats"
set "extra_name=Client Test"

start /wait C:\Python312\Scripts\cxfreeze.exe "server.py" --target-dir "XBDStats"
start /wait C:\Python312\Scripts\cxfreeze.exe "clientTest.py" --target-dir "!extra_name!"

:Start
	"!zip!" a "!archive_name!.zip" "!archive_name!" -mx=7 -r -y
	"!zip!" a "!archive_name!.zip" "!extra_name!" -mx=7 -r -y

	"!zip!" a "!archive_name!.zip" "clientTest_IP.ini" -mx=7 -r -y
	
	(
		echo @Echo off
		echo "XBDStats\server.exe"
	)>"Run XBDStats Server.bat"

	"!zip!" a "!archive_name!.zip" "Run XBDStats Server.bat" -mx=7 -r -y
	del /q "Run XBDStats Server.bat" > NUL
	
	(
		echo @Echo off
		echo start "" "XBDStats\server.exe"
		echo.
		echo if not exist "clientTest_IP.ini" ^(
		echo 	echo ^^[server^^]
		echo 	echo ip=192.168.1.87
		echo ^)^>clientTest_IP.ini
		echo.
		echo start "" "Client Test\clientTest.exe"
	)>"Run XBDStats Server + Client Test.bat"

	"!zip!" a "!archive_name!.zip" "Run XBDStats Server + Client Test.bat" -mx=7 -r -y
	del /q "Run XBDStats Server + Client Test.bat" > NUL

	REM Cleanup
	rmdir /s /q "!archive_name!" > NUL
	rmdir /s /q "!extra_name!" > NUL
