"""
오피넷 Open API 호출 모듈.

인증키는 코드에 적지 않고 프로젝트 루트의 .env 파일에서 읽습니다.
  1) cp .env.example .env
  2) .env 안의 OPINET_API_KEY 값을 본인 키로 수정
  3) pip install -r requirements.txt

사용 예:
  python scripts/opinet.py avgAllPrice
  python scripts/opinet.py pollAvgRecentPrice prodcd=K015
"""
import sys
from pathlib import Path

import requests

BASE_URL = "https://www.opinet.co.kr/api"
ROOT = Path(__file__).resolve().parent.parent


def load_env(path=ROOT / ".env"):
    """.env 파일을 읽어 dict 로 돌려준다. (외부 라이브러리 없이 동작)"""
    if not path.exists():
        template = path.parent / ".env.example"
        if not template.exists():
            raise SystemExit(f"[오류] {path} 도 {template} 도 없습니다.")
        # 처음 실행이면 양식을 복사해 .env 를 대신 만들어 준다.
        path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit(
            f"[안내] {path} 파일을 새로 만들었습니다.\n"
            f"       파일을 열어 XXXX 자리에 인증키를 넣고 저장한 뒤 다시 실행하세요."
        )
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def call(endpoint, **params):
    """오피넷 API 를 호출해 응답 텍스트를 돌려준다.

    인증키는 매 호출마다 code 파라미터로 자동 주입되므로,
    호출하는 쪽에서 키를 다룰 일이 없다.
    """
    key = load_env().get("OPINET_API_KEY", "")
    if not key or key.startswith("XXXX"):
        raise SystemExit("[오류] .env 의 OPINET_API_KEY 가 아직 채워지지 않았습니다.")

    params.setdefault("out", "xml")
    params["code"] = key

    response = requests.get(f"{BASE_URL}/{endpoint}.do", params=params, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def _mask(text, key):
    """화면·로그에 키가 노출되지 않도록 가린다."""
    return text.replace(key, "***KEY***") if key else text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    endpoint = sys.argv[1]
    kwargs = dict(arg.split("=", 1) for arg in sys.argv[2:] if "=" in arg)

    body = call(endpoint, **kwargs)
    print(_mask(body, load_env().get("OPINET_API_KEY", "")))
