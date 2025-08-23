@echo off
echo Windows 작업 스케줄러에 Google Play 리뷰 자동 캡처 작업을 등록합니다...

REM 작업 스케줄러에 등록
schtasks /create /tn "Google Play 리뷰 자동 캡처" /tr "D:\aos review\daily_auto_capture.bat" /sc daily /st 00:05 /ru "SYSTEM" /f

if %errorlevel% equ 0 (
    echo ========================================
    echo 작업 스케줄러 등록 성공!
    echo 작업명: Google Play 리뷰 자동 캡처
    echo 실행 시간: 매일 00:05
    echo 실행 파일: D:\aos review\daily_auto_capture.bat
    echo ========================================
    
    echo 등록된 작업 확인:
    schtasks /query /tn "Google Play 리뷰 자동 캡처"
) else (
    echo ========================================
    echo 작업 스케줄러 등록 실패!
    echo 오류 코드: %errorlevel%
    echo 관리자 권한으로 실행해주세요.
    echo ========================================
)

pause

