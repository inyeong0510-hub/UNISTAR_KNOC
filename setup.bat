@echo off
chcp 949 >nul
cd /d "%~dp0"

if exist ".env" (
    echo [건너뜀] .env 파일이 이미 있습니다. 기존 키를 보호하기 위해 덮어쓰지 않습니다.
) else (
    copy ".env.example" ".env" >nul
    echo [완료] .env 파일을 만들었습니다.
)

echo.
echo 잠시 후 메모장이 열립니다.
echo XXXX 자리에 발급받은 인증키를 붙여넣고 저장하세요.
echo.
pause

notepad ".env"
