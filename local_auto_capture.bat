@echo off
echo ========================================
echo AOS Review 로컬 자동 캡처 시작
echo ========================================

REM Python 가상환경 활성화 (필요시)
REM call venv\Scripts\activate

REM 캡처 스크립트 실행
echo 1. Google Play 리뷰 캡처 실행 중...
python github_actions_capture.py

REM 캡처 성공 여부 확인
if %ERRORLEVEL% EQU 0 (
    echo 2. 캡처 완료! HTML 파일 업데이트 중...
    
    REM Git 상태 확인
    git status --porcelain | findstr "aos_review.html" >nul
    if %ERRORLEVEL% EQU 0 (
        echo 3. HTML 파일 변경 감지! GitHub에 푸시 중...
        
        REM 변경사항 커밋 및 푸시
        git add aos_review.html
        git commit -m "Auto update: $(date /t) $(time /t)"
        git push origin master
        
        echo 4. GitHub 푸시 완료!
        echo 5. GitHub Pages 업데이트 중... (몇 분 소요)
        echo 6. 확인: https://jaeleehong.github.io/aos_review/aos_review.html
    ) else (
        echo 3. HTML 파일 변경 없음. 푸시 건너뜀.
    )
) else (
    echo 2. 캡처 실패! 로그를 확인하세요.
)

echo ========================================
echo 작업 완료!
echo ========================================
pause
