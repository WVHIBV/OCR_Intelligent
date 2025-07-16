; Script Inno Setup pour OCR Intelligent
; Version professionnelle avec installation complète

#define MyAppName "OCR Intelligent"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "OCR Intelligent Team"
#define MyAppURL "https://github.com/ocr-intelligent"
#define MyAppExeName "Lancer_OCR_Intelligent.bat"

[Setup]
; Identifiant unique de l'application
AppId={{A1B2C3D4-E5F6-7890-ABCD-123456789DEF}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/support
AppUpdatesURL={#MyAppURL}/releases
AppCopyright=Copyright (C) 2024 {#MyAppPublisher}

; Configuration d'installation
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=dist
OutputBaseFilename=OCR_Intelligent_Setup_v{#MyAppVersion}
SetupIconFile=ocr_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
InternalCompressLevel=ultra64

; Configuration Windows
MinVersion=10.0.17763
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no

; Interface utilisateur moderne
WizardStyle=modern
WizardSizePercent=120
WizardResizable=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Fichiers principaux de l'application
Source: "main.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "Lancer_OCR_Intelligent.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "port_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "ocr_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "PROJECT_STRUCTURE.md"; DestDir: "{app}"; Flags: ignoreversion

; Dossiers de l'application
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\output"; Flags: uninsalwaysuninstall
Name: "{app}\logs"; Flags: uninsalwaysuninstall
Name: "{app}\corrected"; Flags: uninsalwaysuninstall

[Icons]
; Icône dans le menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\Lancer_OCR_Intelligent.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ocr_icon.ico"
; Icône sur le bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\Lancer_OCR_Intelligent.bat"; WorkingDir: "{app}"; IconFilename: "{app}\ocr_icon.ico"; Tasks: desktopicon
; Icône de désinstallation
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Lancer_OCR_Intelligent.bat"; Description: "Lancer {#MyAppName} maintenant"; Flags: nowait postinstall skipifsilent; Check: CheckPythonInstalled

[Code]
function CheckPythonInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Vérifier si Python est accessible via PATH
  if Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
      Result := True
    else
      Result := False;
  end
  else
    Result := False;
end;

function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
  PythonPath: string;
  MsgText: string;
begin
  GetWindowsVersionEx(Version);

  if Version.Major < 10 then
  begin
    MsgBox('Ce logiciel nécessite Windows 10 ou plus récent.', mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Vérifier si Python est installé
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.9\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\Python\PythonCore\3.8\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Python\PythonCore\3.9\InstallPath', '', PythonPath) and
     not RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Python\PythonCore\3.8\InstallPath', '', PythonPath) then
  begin
    MsgText := 'ATTENTION: Python n''est pas détecté sur votre système.' + #13#10#13#10 +
               'OCR Intelligent nécessite Python 3.8 ou supérieur pour fonctionner.' + #13#10#13#10 +
               'Après l''installation, vous devrez:' + #13#10 +
               '1. Télécharger Python depuis https://python.org' + #13#10 +
               '2. Cocher "Add Python to PATH" lors de l''installation' + #13#10 +
               '3. Redémarrer votre ordinateur' + #13#10#13#10 +
               'Voulez-vous continuer l''installation ?';

    if MsgBox(MsgText, mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
      Result := False
    else
      Result := True;
  end
  else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Créer un fichier d'information pour l'utilisateur
    SaveStringToFile(ExpandConstant('{app}\LIRE_MOI_INSTALLATION.txt'),
      'OCR Intelligent a été installé avec succès !' + #13#10#13#10 +
      'Pour utiliser l''application:' + #13#10 +
      '1. Double-cliquez sur "OCR Intelligent" sur votre bureau' + #13#10 +
      '   OU utilisez le raccourci dans le menu Démarrer' + #13#10#13#10 +
      'Si Python n''est pas installé:' + #13#10 +
      '1. Téléchargez Python depuis https://python.org' + #13#10 +
      '2. Cochez "Add Python to PATH" lors de l''installation' + #13#10 +
      '3. Redémarrez votre ordinateur' + #13#10 +
      '4. Lancez OCR Intelligent' + #13#10#13#10 +
      'L''application installera automatiquement toutes les dépendances nécessaires.' + #13#10#13#10 +
      'Support: Consultez README.md dans le dossier d''installation',
      False);
  end;
end;
