@echo off
REM 한셀 변환기 실행 스크립트

echo ========================================
echo 한셀 파일 일괄 변환기 실행
echo ========================================
echo.

REM 가상 환경 활성화 및 실행
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python app.py
) else (
    echo [오류] 가상 환경이 없습니다.
    echo setup.bat을 먼저 실행하세요.
    pause
    exit /b 1
)
