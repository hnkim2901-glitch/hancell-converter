@echo off
REM 한셀 변환기 설치 스크립트

echo ========================================
echo 한셀 파일 일괄 변환기 설치
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치한 후 다시 실행하세요.
    pause
    exit /b 1
)

echo [1/3] Python 버전 확인...
python --version

echo.
echo [2/3] 가상 환경 생성...
python -m venv venv

echo.
echo [3/3] 의존성 설치...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo ========================================
echo 설치가 완료되었습니다!
echo.
echo 실행 방법:
echo   1. run.bat 실행
echo   또는
echo   2. venv\Scripts\activate.bat
echo      python app.py
echo ========================================
pause
