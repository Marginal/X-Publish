; NSIS installation

;--------------------------------
!include "MUI.nsh"

!define MUI_ABORTWARNING

SetCompressor /SOLID lzma

Name "X-Publish $%VERSION%"
Caption "X-Publish $%VERSION% Installer"
OutFile "X-Publish_$%VER%_win32.exe"
InstallDir "$PROGRAMFILES\X-Publish"
BrandingText "http://marginal.org.uk/x-planescenery"

; !insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; !insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Icon "win32\installer.ico"
UninstallIcon "win32\installer.ico"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r dist\*
  Delete "$INSTDIR\X-Publish.exe.log"
  CreateShortCut "$SMPROGRAMS\X-Publish.lnk" "$INSTDIR\xpublish.exe"

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "DisplayIcon" "$INSTDIR\X-Publish.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "DisplayName" "X-Publish"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "DisplayVersion" "$%VERSION%"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "Publisher" "Jonathan Harris <x-plane@marginal.org.uk>"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "NoRepair" 1
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\OverlayEditor" "URLInfoAbout" "mailto:Jonathan Harris <x-plane@marginal.org.uk>?subject=X-Publish $%VERSION%"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish" "URLUpdateInfo" "http://marginal.org.uk/x-planescenery"

WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd


Section "Uninstall"
  Delete "$SMPROGRAMS\X-Publish.lnk"
  Delete "$INSTDIR\MSVCR71.dll"
  Delete "$INSTDIR\X-Publish.exe"
  Delete "$INSTDIR\X-Publish.exe.log"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\X-Publish"
SectionEnd
