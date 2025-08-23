@echo off
echo ========================================
echo Google Play 리뷰 자동 캡처 시스템 상태 확인
echo ========================================

echo.
echo 1. 작업 스케줄러 상태 확인:
schtasks /query /tn "Google Play 리뷰 자동 캡처" /fo table

echo.
echo 2. 최근 로그 확인:
if exist "logs\auto_capture_%date:~0,4%%date:~5,2%%date:~8,2%.log" (
    echo 최근 로그 파일: logs\auto_capture_%date:~0,4%%date:~5,2%%date:~8,2%.log
    echo 마지막 10줄:
    powershell "Get-Content 'logs\auto_capture_%date:~0,4%%date:~5,2%%date:~8,2%.log' | Select-Object -Last 10"
) else (
    echo 로그 파일이 없습니다.
)

echo.
echo 3. 캡처된 폴더 확인:
dir "D:\aos review" /b /ad | findstr /r "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$"

echo.
echo 4. HTML 파일 존재 확인:
if exist "D:\aos review\구글 플레이_리뷰.html" (
    echo HTML 파일 존재: 구글 플레이_리뷰.html
) else (
    echo HTML 파일이 없습니다!
)

echo.
echo 5. Python 환경 확인:
python --version
pip list | findstr selenium
pip list | findstr Pillow

echo.
echo ========================================
pause



