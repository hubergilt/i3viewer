!define APP_NAME "MPROUTER_3D_Viewer"
!define APP_VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!define EXE_NAME "3dviewer.exe"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

Outfile "${APP_NAME}_Installer.exe"
Icon "dist/3dviewer.ico"
UninstallIcon "dist/3dviewer.ico"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy application files
    File /r "dist\*"

    File "dist/3dviewer.ico"
    ; Create Start Menu and Desktop shortcuts
    CreateShortcut "$SMPROGRAMS\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}" "" "$INSTDIR\3dviewer.ico"
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${EXE_NAME}" "" "$INSTDIR\3dviewer.ico"

    ; Install Visual C++ Redistributable if needed
    ; ExecWait '"$INSTDIR\vc_redist.x64.exe" /quiet /norestart' ; Modify if using a different version

    ; Add uninstall entry to the Windows registry
    WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "${UNINSTALL_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${UNINSTALL_KEY}" "NoRepair" 1

    ; Create an uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove installed files
    Delete "$INSTDIR\${EXE_NAME}"
    ; Delete "$INSTDIR\vc_redist.x64.exe"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\${APP_NAME}.lnk"
    Delete "$DESKTOP\${APP_NAME}.lnk"

    ; Remove install directory
    RMDir /r "$INSTDIR"

    ; Remove uninstall entry from the registry
    DeleteRegKey HKLM "${UNINSTALL_KEY}"
SectionEnd
