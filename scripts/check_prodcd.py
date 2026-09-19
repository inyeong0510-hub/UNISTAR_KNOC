"""
Mission 1 ① 검증용 — 자동차부탄 제품코드 K015 / K105 실태 확인.

오피넷 API 가이드(2026.06) 안에서 같은 제품인 '자동차부탄'이
  · K105 로 적힌 곳 : p8 pollAvgRecentPrice, p9 areaAvgRecentPrice,
                      p22 datePollAvgRecentPrice, p23 dateAreaAvgRecentPrice
  · K015 로 적힌 곳 : 나머지 9개 API 전부
로 갈려 있다. 어느 쪽이 실제로 유효한지 호출로 확인한다.

사용법:  python scripts/check_prodcd.py
결과는 evidence/prodcd_check_<날짜>.txt 로 저장된다(증빙 첨부용).
"""
from datetime import datetime
from pathlib import Path

from opinet import call

ROOT = Path(__file__).resolve().parent.parent

# 가이드에서 K105 로 표기된 엔드포인트들
TARGETS = ["pollAvgRecentPrice", "areaAvgRecentPrice"]
CODES = ["K015", "K105"]


def summarize(body):
    """응답이 실제 데이터인지, 빈 결과인지, 오류인지 한 줄로 요약한다."""
    if "<OIL>" in body or "<OIL_" in body:
        return f"데이터 있음 (길이 {len(body)}자)"
    if "ERROR" in body.upper() or "error" in body:
        return f"오류 응답 → {body.strip()[:120]}"
    return f"빈 결과 (길이 {len(body)}자)"


if __name__ == "__main__":
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"자동차부탄 제품코드 검증 — {stamp}", "=" * 60]

    for endpoint in TARGETS:
        extra = {"area": "01"} if endpoint == "areaAvgRecentPrice" else {}
        for code in CODES:
            try:
                result = summarize(call(endpoint, prodcd=code, **extra))
            except Exception as exc:
                result = f"호출 실패 → {exc}"
            line = f"{endpoint:<24} prodcd={code}  →  {result}"
            print(line)
            lines.append(line)
        lines.append("-" * 60)

    out = ROOT / "evidence" / f"prodcd_check_{datetime.now():%Y%m%d}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n증빙 저장: {out.relative_to(ROOT)}")
