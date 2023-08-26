@echo off

%1 mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/c %~s0 ::","","runas",1)(window.close)&&exit

cd /d %~dp0

set StartupPath=%programdata%\Microsoft\Windows\Start Menu\Programs\Startup
mklink "%StartupPath%\CountdownerStartup.lnk" "%cd%\countdowner.exe"

echo Startup Set

timeout /t 5