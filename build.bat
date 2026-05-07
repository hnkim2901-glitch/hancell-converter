@echo off
REM 한셀 변환기 exe 빌드 스크립트

echo ========================================
echo 한셀 파일 일괄 변환기 빌드
echo ========================================
echo.

REM 가상 환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [오류] 가상 환경이 없습니다.
    echo setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

echo [1/2] PyInstaller 설치 확인...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
)

echo.
echo [2/2] exe 파일 빌드 중...
pyinstaller hancell-converter.spec

echo.
echo ========================================
echo 빌드가 완료되었습니다!
echo.
echo 실행 파일 위치:
echo   dist\한셀변환기.exe
echo ========================================
pause
