; Inno Setup 스크립트
; 한셀 파일 일괄 변환기 Installer
;
; 사용법:
; 1. Inno Setup 다운로드: https://jrsoftware.org/isdl.php
; 2. 이 파일을 Inno Setup Compiler로 열기
; 3. Compile 버튼 클릭
; 4. installer_output/ 폴더에 setup.exe 생성됨

#define MyAppName "한셀 파일 일괄 변환기"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://github.com/yourusername/hancell-converter"
#define MyAppExeName "한셀변환기.exe"

[Setup]
; 고유 ID (한 번 생성하면 변경하지 말 것)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 설치 경로
DefaultDirName={autopf}\HancellConverter
DisableProgramGroupPage=yes

; 출력 설정
OutputDir=installer_output
OutputBaseFilename=HancellConverter-Setup-v{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; 압축
Compression=lzma2/ultra64
SolidCompression=yes

; UI
WizardStyle=modern

; 권한 (관리자 권한 불필요)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 라이선스
LicenseFile=LICENSE

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 메인 실행 파일
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 문서
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 시작 메뉴
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} 사용 가이드"; Filename: "{app}\README.md"

; 바탕화면
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 설치 완료 후 실행 옵션
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 제거 시 생성된 폴더도 삭제
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\screenshots"
Type: filesandordirs; Name: "{app}\output"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Windows 버전 체크
  if not IsWindows10OrLater() then
  begin
    MsgBox('이 프로그램은 Windows 10 이상이 필요합니다.', mbError, MB_OK);
    Result := False;
  end;
end;

function IsWindows10OrLater(): Boolean;
begin
  Result := (GetWindowsVersion >= $0A000000);
end;
