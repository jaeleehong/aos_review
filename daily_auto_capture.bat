@echo off
cd /d "D:\aos review"
echo ========================================
echo 자동 Google Play 리뷰 캡처 시작
echo 실행 시간: %date% %time%
echo ========================================
python auto_capture_and_update.py
echo ========================================
echo 자동 캡처 완료
echo 완료 시간: %date% %time%
echo ========================================
pause
