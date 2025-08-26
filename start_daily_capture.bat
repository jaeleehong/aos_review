@echo off
echo ========================================
echo 새벽 1시 자동 캡처 스케줄러 시작
echo ========================================
echo.

cd /d "D:\aos_review"

echo 현재 디렉토리: %CD%
echo 현재 시간: %date% %time%
echo.

echo Python 스케줄러를 시작합니다...
echo 종료하려면 Ctrl+C를 누르세요
echo.

python daily_capture_scheduler.py

echo.
echo 스케줄러가 종료되었습니다.
pause

