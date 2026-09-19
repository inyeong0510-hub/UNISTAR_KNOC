"""
Mission 1 ② 증빙용 — 공공데이터포털 개방목록 98건 ↔ 내려받은 원본 파일 대조.

`docs/개방목록_98건.csv` 의 98개 목록과 `data/raw/` 의 실제 파일을 1:1로 맞춰
  · 확보 완료 목록
  · 누락 목록 (무엇이 왜 빠졌는지)
  · 목록 1건에 파일이 여러 개 대응하는 경우
를 표로 정리한다. 파일은 읽지 않고 이름만 대조한다(내용 불변).

매핑은 사람이 확인해 아래 MAPPING 에 명시했다(자동 문자열 유사도 아님).
목록명과 내려받은 파일명이 다른 경우가 많아 자동 매칭은 오탐이 난다.
  예) 목록 "LPG용기충전소 제품별 판매가격"  ↔  파일 "LPG충전소_제품별_평균판매가격.csv"
      목록 "제품별 유류세 변동 내역"        ↔  파일 "세금변동추이.xls"

사용법:  python scripts/reconcile.py
결과는 evidence/reconcile_<날짜>.{csv,md} 로 저장된다(증빙 첨부용).
"""
import csv
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST_CSV = ROOT / "docs" / "개방목록_98건.csv"
RAW = ROOT / "data" / "raw"

# 목록 행번호(1~98) → 대응하는 data/raw 파일명 목록.
# 빈 리스트 = 아직 내려받지 않음. API 행은 파일이 없는 것이 정상이므로 제외 처리.
MAPPING = {
    1: [],                                                      # 빗물이용시설 운영자료(xlsx)
    5: [],                                                      # 무인잠수정(ROV) 사진(jpg)
    6: [],                                                      # 오늘의 뉴스(일일석유뉴스)(pdf)
    8: [],                                                      # 국내대륙붕 석유개발 기술자료 목록
    13: [],                                                     # 가격자유화이전 정유사 가격정보
    14: [],                                                     # 주유소지역상표별통계
    15: [],                                                     # 공공데이터 목록 현황 정보
    16: [], 17: [], 18: [],                                     # 교육영상(mp4) — .gitignore 대상
    19: [],                                                     # 석유개발 기술자료 공개 제도(pdf)
    20: [],                                                     # 공공데이터 활용 가이드북(pdf)
    21: ["한국석유공사_상표권 보유 현황_20260610.csv"],
    22: ["한국석유공사_세계 원유 수출입 물량_20250710.csv"],
    23: ["한국석유공사_세계 석유제품 수출입 물량_20250710.csv"],
    24: ["한국석유공사_세계석유 공급현황(지역별 석유 매장량)_20250804.csv"],
    25: ["한국석유공사_세계석유 공급현황(주요국별 석유 매장량)_20250710.csv"],
    26: ["한국석유공사_세계석유 공급현황(주요국별 석유 생산량)_20250710.csv"],
    27: ["한국석유공사_세계석유 수요현황(세계 석유소비량 추이)_20250804.csv"],
    28: ["한국석유공사_세계석유 수요현황(주요국 일인당 석유소비량)_20250710.csv"],
    29: [],                                                     # 안전한국훈련 사전영상(mp4)
    30: ["한국석유공사_용수 사용량_20241231.csv"],
    31: ["한국석유공사_폐기물 발생량_20250708.csv"],
    32: ["한국석유공사_저공해 자동차 구매임차 현황_20251231.csv"],
    33: ["한국석유공사_저공해 자동차 보유현황_20251231.csv"],
    34: ["한국석유공사_에너지 사용량_20241231.csv"],
    35: ["한국석유공사_온실가스 감축실적_20241231.csv"],
    36: ["지속가능경영보고서 25년_한국석유공사.pdf"],
    37: ["한국석유공사_인천지역 등유 가격 현황_20260430.csv"],
    38: ["한국석유공사_인천지역 경유 가격 현황_20260430.csv"],
    39: ["한국석유공사_인천지역 휘발유 가격 현황_20260430 (1).csv"],
    40: ["한국석유공사_인천지역 주유소 위치 현황_20240530.csv"],
    41: ["한국석유공사_대전 석유제품 소비량_20251231.csv"],
    42: ["한국석유공사_유통단계별 석유제품 소비 비율_20251231.csv"],
    43: ["한국석유공사_비축지사 주소_20230830.csv"],
    44: ["한국석유공사_지역별 자동차충전소 개수_20230830.csv"],
    45: ["한국석유공사_제주 석유제품 소비량_20251231.csv"],
    46: ["한국석유공사_제주 석유제품 연간 소비량_20251231.csv"],
    47: ["한국석유공사_주유소 요소수 평균판매가격_상표별_20260630.csv"],
    48: ["한국석유공사_주유소 요소수 평균판매가격_지역별_20260630.csv"],
    49: ["세금변동추이.xls"],                                    # 제품별 유류세 변동 내역
    50: ["자동차충전소_상표별_평균판매가격.csv"],
    51: ["자동차충전소_지역별_평균판매가격.csv"],
    52: ["자동차충전소_제품별_평균판매가격.csv"],                  # 전국 평균 = 제품별 파일
    53: ["주유소_상표별_면세유평균판매가격.csv"],
    54: ["주유소_지역별_면세유평균판매가격.csv"],
    55: ["주유소_제품별_면세유평균판매가격.csv"],
    56: ["한국석유공사_수의계약정보공개_20251231.csv"],
    57: ["한국석유공사_수의계약업체_20251231.csv"],
    58: ["한국석유공사_행정처분공표통계_20210805.csv"],
    59: ["전자상거래.csv"],                                       # 석유제품 전자상거래 가격
    60: ["한국석유공사_지역별 직영 주유소 비율_20220329.csv"],
    61: ["한국석유공사_알뜰주유소 현황_20251231.csv"],
    62: [],                                                      # 일반 석유상식(PDF)
    63: ["한국석유공사_석유제품수출_국가별_20251231.csv"],
    64: ["한국석유공사_석유제품수입_제품별_20241231.csv"],
    65: ["한국석유공사_석유제품수출_제품별_20251231.csv"],
    66: ["한국석유공사_석유제품수입_국가별_20241231.csv"],
    67: ["한국석유공사_국내 원유수입_국가별_20251231.csv"],
    68: ["한국석유공사_국내 원유수입_유질별_20251231.csv"],
    69: ["한국석유공사_국내 석유제품 제품별 소비현황_20251231.csv"],
    70: ["한국석유공사_국내 석유제품 산업별 소비현황_20251231.csv"],
    71: ["한국석유공사_국내 석유제품 지역별 소비현황_20251231.csv"],
    72: ["한국석유공사_국내 석유제품 생산 현황_20251231.csv"],
    73: ["한국석유공사_국내석유제품재고_20251231.csv"],
    74: ["한국석유공사_국내 석유비축일수_20251231.csv"],
    75: ["한국석유공사_국내 석유비축시설 및 비축물량_20251231.csv"],
    76: ["한국석유공사_석유 정제가동율 현황_20251231.csv"],
    77: ["정제능력(정유사별).csv"],
    78: ["과거_판매가격(주유소)20260918-20260918.csv"],            # 국내 전국 개별 주유소 판매가격
    79: ["대리점_평균판매가격.csv"],                               # 석유대리점 평균판매가격
    80: ["주유소_상표별_평균판매가격.csv"],
    81: ["주유소_지역별_평균판매가격.csv"],
    82: ["주유소_형태별_평균판매가격.csv"],
    83: ["LPG충전소_제품별_평균판매가격.csv"],
    84: ["LPG충전소_지역별_평균판매가격.csv"],
    85: ["LPG판매소_제품별_평균판매가격.csv"],
    86: ["LPG판매소_지역별_평균판매가격.csv"],
    87: ["LPG집단공급사업자_제품별_평균판매가격.csv"],              # 집단공급사업자 평균 = 제품별
    88: ["LPG집단공급사업자_회사별_평균판매가격.csv"],
    89: ["LPG집단사업소_지역별_평균판매가격.csv"],
    90: ["LPG판매소_회사별_평균판매가격.csv"],
    91: ["LPG충전소_회사별_평균판매가격.csv"],
    92: ["정유사_주간공급가격_회사별.csv"],
    93: ["정유사_월간판매가격_회사별.csv"],
    94: ["정유사_월간판매가격_제품별.csv"],
    95: ["정유사_주간공급가격_제품별.csv"],
    96: ["주유소_평균판매가격_제품별.csv"],
    97: [                                                        # 국내석유제품 가격 동향(PDF) — 회차별 3개
        "월간국내유가동향_26년8월(1).pdf",
        "주간국내유가동향_9월_1주(1).pdf",
        "주간국내유가동향_9월_2주(1).pdf",
    ],
    98: ["한국석유공사_지역별 주유소 수_20251231.csv"],
}

# 영상(mp4)은 .gitignore 로 저장소에서 제외한다 → 확보 목표에서 뺀다.
VIDEO_ROWS = {16, 17, 18, 29}


def load_list():
    with LIST_CSV.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def local_files():
    return {
        unicodedata.normalize("NFC", p.name)
        for p in RAW.iterdir()
        if p.is_file() and p.name != ".gitkeep"
    }


def build(rows, present):
    out, used = [], []
    for i, r in enumerate(rows, 1):
        files = [unicodedata.normalize("NFC", f) for f in MAPPING.get(i, [])]
        missing_on_disk = [f for f in files if f not in present]
        if r["구분"] == "API":
            state = "API(파일없음)"
        elif i in VIDEO_ROWS:
            state = "영상(대상제외)"
        elif not files:
            state = "누락"
        elif missing_on_disk:
            state = "매핑오류"
        else:
            state = "확보"
        used += files
        out.append({
            "번호": i,
            "구분": r["구분"],
            "확장자": r["확장자"],
            "목록명": r["목록명"].strip(),
            "상태": state,
            "대응파일": " / ".join(files),
            "대응개수": len(files),
            "URL": r["URL"],
        })
    return out, used


def main():
    rows = load_list()
    present = local_files()
    table, used = build(rows, present)

    dup = [f for f, n in Counter(used).items() if n > 1]
    unmapped = sorted(present - set(used))
    broken = [r for r in table if r["상태"] == "매핑오류"]

    state = Counter(r["상태"] for r in table)
    target = len(table) - state["API(파일없음)"] - state["영상(대상제외)"]
    got = state["확보"]
    multi = [r for r in table if r["대응개수"] > 1]

    summary = [
        f"- 개방목록 전체: {len(table)}건 (파일 {sum(1 for r in table if r['구분']=='파일')} / API {state['API(파일없음)']})",
        f"- 확보 목표(영상 {state['영상(대상제외)']}건 제외): **{target}건**",
        f"- 확보 완료: **{got}건** / 누락: **{state['누락']}건**",
        f"- data/raw 실제 파일: {len(present)}개 "
        f"(목록 1건에 파일 여러 개가 대응하는 경우 {len(multi)}건 → 파일 수 {sum(r['대응개수'] for r in multi)}개)",
        f"- 매핑되지 않은 파일: {len(unmapped)}개" + (f" — {unmapped}" if unmapped else ""),
        f"- 같은 파일이 두 목록에 중복 매핑: {len(dup)}개" + (f" — {dup}" if dup else ""),
        f"- 매핑표에 적었으나 디스크에 없는 파일: {len(broken)}건",
    ]

    stamp = datetime.now().strftime("%Y%m%d")
    fields = ["번호", "구분", "확장자", "목록명", "상태", "대응파일", "대응개수", "URL"]
    csv_out = ROOT / "evidence" / f"reconcile_{stamp}.csv"
    with csv_out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(table)

    md = [
        f"# 개방목록 98건 ↔ 내려받은 파일 대조 — {datetime.now():%Y-%m-%d %H:%M}",
        "",
        "기준 목록: `docs/개방목록_98건.csv` · 대상: `data/raw/`",
        "",
        "## 요약",
        *summary,
        "",
        "## 누락 목록 (내려받아야 할 것)",
        "",
        "| 번호 | 확장자 | 목록명 | URL |",
        "|---|---|---|---|",
    ]
    for r in table:
        if r["상태"] == "누락":
            md.append(f"| {r['번호']} | {r['확장자']} | {r['목록명']} | {r['URL']} |")
    md += [
        "",
        "## 목록 1건 ↔ 파일 다수",
        "",
        "| 번호 | 목록명 | 파일 |",
        "|---|---|---|",
    ]
    for r in multi:
        md.append(f"| {r['번호']} | {r['목록명']} | {r['대응파일']} |")
    md += [
        "",
        "## 전체 대조표",
        "",
        "| " + " | ".join(fields[:-1]) + " |",
        "|" + "|".join(["---"] * (len(fields) - 1)) + "|",
    ]
    for r in table:
        md.append("| " + " | ".join(str(r[f]) for f in fields[:-1]) + " |")

    md_out = ROOT / "evidence" / f"reconcile_{stamp}.md"
    md_out.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(summary))
    print("\n[누락]")
    for r in table:
        if r["상태"] == "누락":
            print(f"  {r['번호']:3d} ({r['확장자']}) {r['목록명']}")
    print(f"\n증빙 저장:\n  {csv_out.relative_to(ROOT)}\n  {md_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
