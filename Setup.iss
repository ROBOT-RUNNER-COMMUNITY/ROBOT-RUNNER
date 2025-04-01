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
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs
Source: "style\*"; DestDir: "{app}\style"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Robot Test Runner"; Filename: "{app}\main.exe"
Name: "{commondesktop}\Robot Test Runner"; Filename: "{app}\main.exe"
