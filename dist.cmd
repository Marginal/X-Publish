@echo off
@setlocal

for /f "usebackq tokens=1,2,3" %%I in (`c:\Progra~1\Python24\python.exe -c "from version import appversion; print '%%4.2f %%d'%%(appversion, round(appversion*100,0))"`) do (set VERSION=%%I&set VER=%%J)
set RELEASE=1
set RPM=%TMP%\xpublish

@if exist X-Publish_%VER%_src.zip del X-Publish_%VER%_src.zip
@if exist X-Publish-%VERSION%-%RELEASE%.noarch.rpm del X-Publish-%VERSION%-%RELEASE%.noarch.rpm
@if exist X-Publish_%VERSION%-%RELEASE%_all.deb del X-Publish_%VERSION%-%RELEASE%_all.deb
@if exist X-Publish_%VER%_mac.zip del X-Publish_%VER%_mac.zip
@if exist X-Publish_%VER%_win32.exe del X-Publish_%VER%_win32.exe

if exist X-Publish.app rd /s /q X-Publish.app
if exist "%RPM%" rd /s /q "%RPM%"
REM >nul: 2>&1
if exist dist rd /s /q dist >nul:  2>&1
REM del /s /q *.bak >nul: 2>&1
del /s /q *.pyc >nul: 2>&1

@set PY=xpublish.py files.py utils.py version.py

:source
REM zip -r X-Publish_%VER%_src.zip dist.cmd %PY% %DATA% %RSRC% %PREV% linux MacOS win32 |findstr -vc:"adding:"

:linux
REM tar -zcf X-Publish_%VER%_linux.tar.gz %PY% %DATA% %RSRC% linux win32/bglunzip.exe win32/DSFTool.exe
set RPMRT=%TMP%\xpublish\root
mkdir "%RPM%\BUILD"
mkdir "%RPM%\SOURCES"
mkdir "%RPM%\RPMS\noarch"
mkdir "%RPMRT%\usr\local\bin"
mkdir "%RPMRT%\usr\local\lib\xpublish"
copy linux\xpublish.desktop "%RPMRT%\usr\local\lib\xpublish" |findstr -v "file(s) copied"
copy linux\X-Publish.xpm "%RPM%\SOURCES" |findstr -v "file(s) copied"
echo BuildRoot: /tmp/xpublish/root > "%RPM%\xpublish.spec"
echo Version: %VERSION% >> "%RPM%\xpublish.spec"
echo Release: %RELEASE% >> "%RPM%\xpublish.spec"
type linux\xpublish.spec    >> "%RPM%\xpublish.spec"
copy linux\xpublish "%RPMRT%\usr\local\bin" |findstr -v "file(s) copied"
for %%I in (%PY%) do (copy %%I "%RPMRT%\usr\local\lib\xpublish" |findstr -v "file(s) copied")
copy linux\X-Publish.png "%RPMRT%\usr\local\lib\xpublish" |findstr -v "file(s) copied"
"C:\Program Files\cygwin\lib\rpm\rpmb.exe" --quiet -bb --target noarch-pc-linux --define '_topdir /tmp/xpublish' /tmp/xpublish/xpublish.spec
move "%RPM%\RPMS\noarch\xpublish-%VERSION%-%RELEASE%.cygwin.noarch.rpm" xpublish-%VERSION%-%RELEASE%.noarch.rpm
REM Debian/Ubuntu
mkdir "%RPMRT%\DEBIAN"
mkdir "%RPMRT%\usr\local\share\applications"
mkdir "%RPMRT%\usr\local\share\icons\hicolor\48x48\apps"
copy linux\xpublish.desktop "%RPMRT%\usr\local\share\applications" |findstr -v "file(s) copied"
copy linux\X-Publish.png "%RPMRT%\usr\local\share\icons\hicolor\48x48\apps\X-Publish.png" |findstr -v "file(s) copied"
echo Version: %VERSION%-%RELEASE% > "%RPMRT%\DEBIAN\control"
type linux\control >> "%RPMRT%\DEBIAN\control"
copy linux\postinst "%RPMRT%\DEBIAN" |findstr -v "file(s) copied"
chmod -R 755 "%RPMRT%"
for /r "%RPMRT%" %%I in (*) do chmod 644 "%%I"
chmod -R 755 "%RPMRT%\DEBIAN\postinst"
chmod -R 755 "%RPMRT%\usr\local\bin\xpublish"
chown -R root:root "%RPMRT%"
dpkg-deb -b /tmp/xpublish/root .
chown -R %USERNAME% "%RPMRT%"

:mac
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

:win32
if exist build rd /s /q build
"C:\Program Files\Python24\python.exe" -OO win32\setup.py -q py2exe
"C:\Program Files\NSIS\makensis.exe" /nocd /v2 win32\X-Publish.nsi
rd /s /q build

:end
