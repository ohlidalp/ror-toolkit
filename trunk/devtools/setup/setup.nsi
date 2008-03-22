; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Rigs of Rods Toolkit"
!define PRODUCT_VERSION "0.34-rc3"
!define PRODUCT_PUBLISHER "Thomas Fischer"
!define PRODUCT_WEB_SITE "http://wiki.rigsofrods.com/index.php?title=RoRToolkit"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define PYTHONVERSION "2.5"
!define PYTHONDLURL   "http://python.org/ftp/python/2.5.1/python-2.5.1.msi"
!define PYTHONDLFN    "python-2.5.1.msi"

SetCompressor lzma

BrandingText "Rigs of Rods Toolkit"
InstProgressFlags smooth colored
XPStyle on
#ShowInstDetails show
ShowUninstDetails show
SetDateSave on
#SetDatablockOptimize on
CRCCheck on
#SilentInstall normal

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "LogicLib.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install-blue.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall-blue.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "readme-installer.txt"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
;!define MUI_FINISHPAGE_RUN "$INSTDIR\rortoolkit.bat"
;!define MUI_FINISHPAGE_RUN_PARAMETERS ""
#!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\Example.file"

!define MUI_FINISHPAGE_NOAUTOCLOSE
;!define MUI_FINISHPAGE_RUN
;!define MUI_FINISHPAGE_RUN_NOTCHECKED
;!define MUI_FINISHPAGE_RUN_TEXT "Update and start (Can take some time)"
;!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchPostInstallation"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Ukrainian"
!insertmacro MUI_LANGUAGE "Finnish"
!insertmacro MUI_LANGUAGE "Czech"
!insertmacro MUI_LANGUAGE "Italian"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

InstType /NOCUSTOM
InstType "full"
InstType "minimal"
; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "RoRToolkitSetup.exe"
InstallDir "$PROGRAMFILES\Rigs of Rods 0.34 Toolkit"
;InstallDir "c:\rortoolkit"
ShowInstDetails show
ShowUnInstDetails show

Var /GLOBAL PYOK
Var /GLOBAL PYPATH
Var /GLOBAL PYINSTALLED

Function DetectPython
     ReadRegStr $R6 HKCU "SOFTWARE\Python\PythonCore\${PYTHONVERSION}\InstallPath" ""
     ${If} $R6 == ''
         ReadRegStr $R6 HKLM "SOFTWARE\Python\PythonCore\${PYTHONVERSION}\InstallPath" ""
         ${If} $R6 == ''
             Push "No registry key found"
             Push "NOK"
             Return
         ${EndIf}
     ${EndIf}

     ${If} ${FileExists} "$R6\python.exe"
         Push "$R6"
         Push "OK"
     ${Else}
         Push "No python.exe found"
         Push "NOK"
     ${EndIf}
FunctionEnd

Function CheckForPython
  Banner::show /NOUNLOAD "Checking for Python ${PYTHONVERSION} ..."
  StrCpy $PYINSTALLED ""
  Call DetectPython
  Pop $PYOK
  Pop $PYPATH
  Banner::destroy
  ${If} $PYOK == 'OK'
        DetailPrint "Detected Python ${PYTHONVERSION}!"
        Return
  ${Else}
        MessageBox MB_YESNOCANCEL|MB_ICONEXCLAMATION "The installer cannot find Python ${PYTHONVERSION}!$\r$\nWould you like the installer to download and install Python ${PYTHONVERSION} for you?" IDNO abort IDCANCEL abort
        DetailPrint "Downloading ${PYTHONDLURL}..."

        NSISdl::download ${PYTHONDLURL} ${PYTHONDLFN}
        Pop $R0 ;Get the return value
        StrCmp $R0 "success" dlok abort
        dlok:
                DetailPrint "Installing Python ${PYTHONVERSION}..."
                ExecWait '"msiExec" /q /i "${PYTHONDLFN}"'
                StrCpy $PYINSTALLED ""
                Call DetectPython
                Pop $PYOK
                Pop $PYPATH
                ${If} $PYOK == 'OK'
                       DetailPrint "Detected Python ${PYTHONVERSION}!"
                       Return
                ${Else}
                       MessageBox MB_OK "Python ${PYTHONVERSION} installation failed! Please install by hand and restart this installation!"
                       Abort
                ${EndIf}
                Return
  ${EndIf}
  Return
  abort:
        MessageBox MB_OK "Please install Python ${PYTHONVERSION} and retry this installation!"
        Abort
FunctionEnd

#Function InstallDirectX
#        InitPluginsDir
#        File /oname=$PLUGINSDIR\dxwebsetup.exe "..\..\tools\3rdparty\dxwebsetup.exe"
#        Banner::show /NOUNLOAD "Installing lastest DirectX ..."
#        ExecWait '"$PLUGINSDIR\dxwebsetup.exe /Q"'
#        Delete $PLUGINSDIR\dxwebsetup.exe
#        Banner::destroy
#FunctionEnd


#Function InstallPyWin32
#        InitPluginsDir
#        File /oname=$PLUGINSDIR\pywin32-setup.exe "..\..\tools\3rdparty\pywin32-setup.exe"
#        Banner::show /NOUNLOAD "Installing Python for Windows ..."
#        ExecWait '"$PLUGINSDIR\pywin32-setup.exe"'
#        Delete $PLUGINSDIR\pywin32-setup.exe
#        Banner::destroy
#FunctionEnd

#Function InstallPyParsing
#        InitPluginsDir
#        File /oname=$PLUGINSDIR\pyparsing-1.4.6.win32.exe "..\..\tools\3rdparty\pyparsing-1.4.6.win32.exe"
#        Banner::show /NOUNLOAD "Installing PyParsing Python Module ..."
#        ExecWait '"$PLUGINSDIR\pyparsing-1.4.6.win32.exe"'
#        Delete $PLUGINSDIR\pyparsing-1.4.6.win32.exe
#        Banner::destroy
#FunctionEnd

#Function InstallGraphViz
#        InitPluginsDir
#        File /oname=$PLUGINSDIR\graphviz-2.12.exe "..\..\tools\3rdparty\graphviz-2.12.exe"
#        Banner::show /NOUNLOAD "Installing Graphviz for Windows ..."
#        ExecWait '"$PLUGINSDIR\graphviz-2.12.exe"'
#        Delete $PLUGINSDIR\graphviz-2.12.exe
#        Banner::destroy
#FunctionEnd

#Function ChangeRoRRepoReg
#         Banner::show /NOUNLOAD "Updating RoR Repository Protocol Extensions ..."
#         WriteRegStr HKCR "RoRRepo" "" "URL:RoRRepo Protocol"
#         WriteRegStr HKCR "RoRRepo" "URL Protocol" ""
#         WriteRegStr HKCR "RoRRepo\shell" "" ""
#         WriteRegStr HKCR "RoRRepo\shell\open" "" ""
#         ReadEnvStr $0 SYSTEMDRIVE
#         WriteRegStr HKCR 'RoRRepo\shell\open\command' '' '"$0\python25\python.exe" "$INSTDIR\tools\modtool.py" "installrepo" "%1"'
#         Banner::destroy
#FunctionEnd

#Function .onInit
#        InitPluginsDir
#        File /oname=$PLUGINSDIR\splash.bmp "splash.bmp"
#        advsplash::show 1000 1300 600 -1 $PLUGINSDIR\splash
#        Pop $0
#        Delete $PLUGINSDIR\splash.bmp
#        !insertmacro MUI_LANGDLL_DISPLAY
#FunctionEnd

Section "-Install Python" SEC01
  SectionIn 1 2 RO
  Call CheckForPython
SectionEnd

#Section "Required Tools" SEC02
#  SectionIn 1 2 RO
#  Call InstallDirectX
#SectionEnd

#Section /o "Optional Tools" SEC03
#  AddSize 20000
#  SectionIn 1
#  Call InstallPyWin32
#  Call InstallPyParsing
#  Call InstallGraphViz
#SectionEnd

Section "!RoR Toolkit" SEC04
  SectionIn 1 2 RO
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File /r /x *.pyc /x *.pyo /x doc /x devtools /x 3rdparty /x downloaded /x graphs /x linux /x lib_linux /x tools /x .svn /x lib_linux /x linux /x rortoolkit  /x *.log ..\..\*
SectionEnd


!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "python 2.5"
!insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "required Tools (directX)"
!insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "optional Tools (PyWin32 for bugreporting, PyParsing and GraphViz for Dependency Graphs)"
!insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "the RoR Toolkit. It includes the Truckeditor, Terraineditor and various other tools"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;Function "LaunchPostInstallation"
;  ReadEnvStr $0 SYSTEMDRIVE
;  ExecWait "$0\python25\python.exe $INSTDIR\tools\update.py"
;  ExecWait "$0\python25\python.exe $INSTDIR\rortoolkit.py"
;FunctionEnd

Section -AdditionalIcons
  #ReadEnvStr $0 SYSTEMDRIVE
  SetOutPath $INSTDIR
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateDirectory "$SMPROGRAMS\RoRToolkit"
  CreateShortCut "$SMPROGRAMS\Rigs of Rods Toolkit\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Rigs of Rods Toolkit\Uninstall.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut '$SMPROGRAMS\Rigs of Rods Toolkit\Start Toolkit.lnk' '$INSTDIR\rortoolkit.py' '' '$INSTDIR\ror.ico'
SectionEnd

Section -Post
  #Call ChangeRoRRepoReg
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was uninstalled successfully."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Do you want to uninstall $(^Name)?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  RMDir  "/r" "$INSTDIR"

  RMDir  "/r" "$SMPROGRAMS\RoRToolkit"
  Delete "$STARTMENU.lnk"
  RMDir  "$INSTDIR"
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose false
SectionEnd