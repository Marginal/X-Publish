@echo off
@setlocal

for /f "usebackq tokens=1,2" %%I in (`C:\Progra~1\Python27\python.exe -c "from version import appversion; print '%%4.2f %%d'%%(appversion, round(appversion*100,0))"`) do (set VERSION=%%I&set VER=%%J)

if exist dist  rd /s /q dist
if exist build rd /s /q build
"C:\Program Files (x86)\Python27\python.exe" -OO win32\setup.py -q py2exe
if exist dist\w9xpopen.exe del dist\w9xpopen.exe
"C:\Program Files (x86)\NSIS\makensis.exe" /nocd /v2 win32\X-Publish.nsi
