@echo off
chcp 65001 >nul
echo ========================================
echo AOS 리뷰 수동 캡처 및 배포
echo 실행 시간: %date% %time%
echo ========================================

:: 작업 디렉토리로 이동
cd /d "D:\aos_review"

:: Python 스크립트 실행 (캡처 및 HTML 업데이트)
echo 1. Google Play 리뷰 캡처 및 HTML 업데이트 시작...
python auto_capture_and_update.py
if %errorlevel% neq 0 (
    echo 오류: 캡처 실패
    pause
    exit /b 1
)
echo 캡처 완료!

:: Git 상태 확인 및 변경사항 커밋
echo 2. Git 변경사항 확인...
git add .
if %errorlevel% neq 0 (
    echo 오류: Git add 실패
    pause
    exit /b 1
)

:: 변경사항이 있는지 확인
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo 변경사항이 없습니다.
    pause
    exit /b 0
)

:: 커밋 메시지 생성 (오늘 날짜)
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set today=%%c%%a%%b
set commit_msg=Manual update %today% - Daily capture and HTML update

:: 커밋
echo 3. Git 커밋...
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo 오류: Git commit 실패
    pause
    exit /b 1
)

:: GitHub에 푸시
echo 4. GitHub에 배포...
git push origin master
if %errorlevel% neq 0 (
    echo 오류: Git push 실패
    pause
    exit /b 1
)

echo ========================================
echo 수동 캡처 및 배포 완료!
echo 완료 시간: %date% %time%
echo ========================================

:: 로그 파일에 기록
echo [%date% %time%] 수동 캡처 및 배포 완료 >> logs\manual_deploy.log

pause
