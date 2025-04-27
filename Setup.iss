[Setup]
AppName=Robot Test Runner
AppVersion=1.7.0
DefaultDirName={pf}\Robot Test Runner
DefaultGroupName=Robot Test Runner
OutputDir=output
OutputBaseFilename=RobotTestRunner_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=./images/Logo_exe_grand.ico

[Files]
; App Files
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs
Source: "style\*"; DestDir: "{app}\style"; Flags: ignoreversion recursesubdirs

; Installer Files
Source: "installers\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion
Source: "installers\python-3.10.0-amd64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Run]
; Install Visual C++ Redistributable silently
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing Visual C++ Redistributable..."; Flags: waituntilterminated

; Install Python silently
Filename: "{tmp}\python-3.10.0-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1"; StatusMsg: "Installing Python..."; Flags: waituntilterminated

; Launch your application after installation
Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,Robot Test Runner}"; Flags: nowait postinstall skipifsilent
