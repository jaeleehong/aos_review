@echo off
chcp 65001 >nul
echo ========================================
echo AOS 리뷰 테스트 자동 캡처 및 배포 시작
echo 실행 시간: %date% %time%
echo ========================================

:: 작업 디렉토리로 이동
cd /d "D:\aos_review"

:: 로그 파일에 시작 기록
echo [%date% %time%] 테스트 자동 캡처 시작 >> logs\test_auto_deploy.log

:: Python 스크립트 실행 (캡처 및 HTML 업데이트)
echo 1. Google Play 리뷰 캡처 및 HTML 업데이트 시작...
python auto_capture_and_update.py
if %errorlevel% neq 0 (
    echo 오류: 캡처 실패
    echo [%date% %time%] 테스트 캡처 실패 >> logs\test_auto_deploy.log
    exit /b 1
)
echo 캡처 완료!

:: Git 상태 확인 및 변경사항 커밋
echo 2. Git 변경사항 확인...
git add .
if %errorlevel% neq 0 (
    echo 오류: Git add 실패
    echo [%date% %time%] Git add 실패 >> logs\test_auto_deploy.log
    exit /b 1
)

:: 변경사항이 있는지 확인
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo 변경사항이 없습니다.
    echo [%date% %time%] 변경사항 없음 >> logs\test_auto_deploy.log
    exit /b 0
)

:: 커밋 메시지 생성 (테스트용)
set commit_msg=Test auto update %date% %time% - Test capture and HTML update

:: 커밋
echo 3. Git 커밋...
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo 오류: Git commit 실패
    echo [%date% %time%] Git commit 실패 >> logs\test_auto_deploy.log
    exit /b 1
)

:: GitHub에 푸시
echo 4. GitHub에 배포...
git push origin master
if %errorlevel% neq 0 (
    echo 오류: Git push 실패
    echo [%date% %time%] Git push 실패 >> logs\test_auto_deploy.log
    exit /b 1
)

echo ========================================
echo 테스트 자동 캡처 및 배포 완료!
echo 완료 시간: %date% %time%
echo ========================================

:: 로그 파일에 완료 기록
echo [%date% %time%] 테스트 자동 캡처 및 배포 완료 >> logs\test_auto_deploy.log

exit /b 0
