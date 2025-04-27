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
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin

[Files]
Source: "dist\RobotTestRunner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs
Source: "style\*"; DestDir: "{app}\style"; Flags: ignoreversion recursesubdirs
Source: "python-embed\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\Robot Test Runner"; Filename: "{app}\RobotTestRunner.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\Robot Test Runner"; Filename: "{app}\RobotTestRunner.exe"; WorkingDir: "{app}"

[Run]
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installation de Visual C++ Redistributable..."; Check: VCRedistNeedsInstall
Filename: "{app}\python\initialize.bat"; Description: "Configuration de l'environnement Python"; StatusMsg: "Installation des dépendances Python..."; Flags: runhidden
Filename: "{app}\RobotTestRunner.exe"; Description: "Lancer l'application"; Flags: postinstall nowait skipifsilent

[Code]
function VCRedistNeedsInstall: Boolean;
begin
  // Vérifie si Visual C++ 2015-2022 Redistributable (x64) est installé
  Result := not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Exécuter le script d'initialisation Python après l'installation
    Exec(ExpandConstant('{app}\python\initialize.bat'), '', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;