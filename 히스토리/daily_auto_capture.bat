@echo off
cd /d "D:\aos review"

echo ========================================
echo Google Play 리뷰 자동 캡처 시작
echo 날짜: %date% %time%
echo ========================================

REM Python 스크립트 실행
python auto_capture_and_update.py

REM 실행 결과 확인
if %errorlevel% equ 0 (
    echo ========================================
    echo 자동 캡처 완료 성공!
    echo 날짜: %date% %time%
    echo ========================================
) else (
    echo ========================================
    echo 자동 캡처 실패! 오류 코드: %errorlevel%
    echo 날짜: %date% %time%
    echo ========================================
)

REM 로그 파일에 기록
echo [%date% %time%] 자동 캡처 실행 완료 (오류코드: %errorlevel%) >> auto_capture_log.txt



