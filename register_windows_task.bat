@echo off
echo ========================================
echo Windows 작업 스케줄러 등록
echo ========================================
echo.

echo 현재 사용자: %USERNAME%
echo.

echo 새벽 1시 자동 캡처 작업을 등록합니다...
echo.

REM 기존 작업이 있다면 삭제
schtasks /delete /tn "AOS_Review_Daily_Capture" /f 2>nul

REM 새 작업 등록
schtasks /create /tn "AOS_Review_Daily_Capture" /tr "D:\aos_review\start_daily_capture.bat" /sc daily /st 01:00 /ru "%USERNAME%" /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 작업 스케줄러 등록 성공!
    echo ========================================
    echo 작업 이름: AOS_Review_Daily_Capture
    echo 실행 시간: 매일 새벽 1시
    echo 실행 파일: D:\aos_review\start_daily_capture.bat
    echo.
    echo 등록된 작업을 확인하려면 다음 명령을 실행하세요:
    echo schtasks /query /tn "AOS_Review_Daily_Capture"
) else (
    echo.
    echo ========================================
    echo 작업 스케줄러 등록 실패!
    echo ========================================
    echo 관리자 권한으로 실행해보세요.
)

echo.
pause

