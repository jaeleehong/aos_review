@echo off
chcp 65001 >nul
echo 뉴맞고 테스트 캡처 시작...
echo.

python test_newmatgo_capture.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 뉴맞고 테스트 캡처가 성공적으로 완료되었습니다.
) else (
    echo.
    echo 뉴맞고 테스트 캡처 중 오류가 발생했습니다.
)

echo.
pause

