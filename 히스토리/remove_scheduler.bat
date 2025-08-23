@echo off
echo Windows 작업 스케줄러에서 Google Play 리뷰 자동 캡처 작업을 제거합니다...

REM 작업 스케줄러에서 제거
schtasks /delete /tn "Google Play 리뷰 자동 캡처" /f

if %errorlevel% equ 0 (
    echo ========================================
    echo 작업 스케줄러 제거 성공!
    echo 작업명: Google Play 리뷰 자동 캡처
    echo ========================================
) else (
    echo ========================================
    echo 작업 스케줄러 제거 실패!
    echo 오류 코드: %errorlevel%
    echo 작업이 존재하지 않거나 관리자 권한이 필요합니다.
    echo ========================================
)

pause



