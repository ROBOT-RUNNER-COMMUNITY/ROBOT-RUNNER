[Setup]
AppName=Robot Test Runner
AppVersion=1.7.6
DefaultDirName={pf}\Robot Test Runner
DefaultGroupName=Robot Test Runner
OutputDir=output
OutputBaseFilename=RobotTestRunner_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=./images/Logo_exe_grand.ico

[Files]
Source: "dist\RobotTestRunner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs
Source: "style\*"; DestDir: "{app}\style"; Flags: ignoreversion recursesubdirs
Source: "installers\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: ignoreversion
Source: "installers\python-3.10.0-amd64.exe"; DestDir: "{tmp}"; Flags: ignoreversion

[Run]
Filename: "{tmp}\vc_redist.x64.exe"; StatusMsg: "Installing Visual C++ Redistributable..."; Flags: waituntilterminated
Filename: "{tmp}\python-3.10.0-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"; StatusMsg: "Installing Python 3.10..."; Flags: waituntilterminated skipifdoesntexist
Filename: "{app}\RobotTestRunner.exe"; Description: "Launch RobotTestRunner"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{group}\Robot Test Runner"; Filename: "{app}\RobotTestRunner.exe"
Name: "{commondesktop}\Robot Test Runner"; Filename: "{app}\RobotTestRunner.exe"
