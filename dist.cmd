@echo off
@setlocal

for /f "usebackq tokens=1,2,3" %%I in (`c:\Progra~1\Python24\python.exe -c "from version import appversion; print '%%4.2f %%d'%%(appversion, round(appversion*100,0))"`) do (set VERSION=%%I&set VER=%%J)
set RELEASE=1
set RPM=%TMP%\X-Publish

@if exist X-Publish_%VER%_src.zip del X-Publish_%VER%_src.zip
@if exist X-Publish-%VERSION%-%RELEASE%.i386.rpm del X-Publish-%VERSION%-%RELEASE%.i386.rpm
@if exist X-Publish_%VERSION%-%RELEASE%_i386.deb del X-Publish_%VERSION%-%RELEASE%_i386.deb
@if exist X-Publish_%VER%_mac.zip del X-Publish_%VER%_mac.zip
@if exist X-Publish_%VER%_win32.exe del X-Publish_%VER%_win32.exe

if exist X-Publish.app rd /s /q X-Publish.app
if exist "%RPM%" rd /s /q "%RPM%"
REM >nul: 2>&1
if exist dist rd /s /q dist >nul:  2>&1
REM del /s /q *.bak >nul: 2>&1
del /s /q *.pyc >nul: 2>&1

@set PY=xpublish.py files.py utils.py version.py

@REM source
REM zip -r X-Publish_%VER%_src.zip dist.cmd %PY% %DATA% %RSRC% %PREV% linux MacOS win32 |findstr -vc:"adding:"

@REM mac
mkdir X-Publish.app\Contents
for %%I in (%DATA%) do (copy %%I X-Publish.app\Contents\ |findstr -v "file(s) copied")
xcopy /q /e MacOS X-Publish.app\Contents\MacOS\|findstr -v "file(s) copied"
for /r X-Publish.app %%I in (CVS) do rd /s /q "%%I" >nul: 2>&1
for /r X-Publish.app %%I in (.cvs*) do del /q "%%I" >nul:
for %%I in (%PY%) do (copy %%I X-Publish.app\Contents\MacOS\ |findstr -v "file(s) copied")
mkdir X-Publish.app\Contents\Resources
sed s/appversion/%VERSION%/ <X-Publish.app\Contents\MacOS\Info.plist >X-Publish.app\Contents\Info.plist
del X-Publish.app\Contents\MacOS\Info.plist
move X-Publish.app\Contents\MacOS\X-Publish.icns X-Publish.app\Contents\Resources\
REM move /y X-Publish.app\Contents\MacOS\*.png X-Publish.app\Contents\Resources\ |findstr -vc:".png"
zip -r X-Publish_%VER%_mac.zip X-Publish.app |findstr -vc:"adding:"

@REM win32
"C:\Program Files\Python24\python.exe" -OO win32\setup.py -q py2exe
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\X-Publish.nsi
rd  /s /q build

:end
