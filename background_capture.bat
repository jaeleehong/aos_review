@echo off
chcp 65001 >nul

:: 작업 디렉토리로 이동
cd /d "D:\aos_review"

:: 백그라운드에서 Python 스크립트 실행
echo 백그라운드에서 AOS 리뷰 캡처 시작...
start /min pythonw auto_capture_and_update.py

:: 잠시 대기 후 Git 작업 실행
timeout /t 30 /nobreak >nul

:: Git 상태 확인 및 변경사항 커밋
echo Git 변경사항 확인 중...
git add .
if %errorlevel% neq 0 (
    echo 오류: Git add 실패
    exit /b 1
)

:: 변경사항이 있는지 확인
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo 변경사항이 없습니다.
    exit /b 0
)

:: 커밋 메시지 생성 (오늘 날짜)
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set today=%%c%%a%%b
set commit_msg=Background update %today% - Daily capture and HTML update

:: 커밋
echo Git 커밋 중...
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo 오류: Git commit 실패
    exit /b 1
)

:: GitHub에 푸시
echo GitHub에 배포 중...
git push origin master
if %errorlevel% neq 0 (
    echo 오류: Git push 실패
    exit /b 1
)

echo 백그라운드 캡처 및 배포 완료!
echo 로그는 logs 폴더에서 확인하세요.

exit /b 0
