#!/bin/bash
# macOS / Linux 용 초기 설정 스크립트
cd "$(dirname "$0")"

if [ -f .env ]; then
    echo "[건너뜀] .env 파일이 이미 있습니다. 기존 키를 보호하기 위해 덮어쓰지 않습니다."
else
    cp .env.example .env
    echo "[완료] .env 파일을 만들었습니다."
fi

echo
echo "편집기가 열리면 XXXX 자리에 발급받은 인증키를 붙여넣고 저장하세요."
echo

open -e .env 2>/dev/null || ${EDITOR:-nano} .env
