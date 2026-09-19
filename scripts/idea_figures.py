"""
④ 아이디어 초안(`docs/아이디어_초안_10건.md`)에 인용한 숫자를 재현한다.

제출 전에 본인이 숫자를 직접 확인할 수 있어야 하므로, 초안에 쓴 값이
어느 파일 어느 계산에서 나왔는지 그대로 다시 출력한다.
읽기만 하고 아무것도 바꾸지 않는다.

사용법:  python scripts/idea_figures.py
"""
import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"


def rd(name):
    with (P / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.reader(fh))


def head(n, title):
    print(f"\n{'='*66}\n[{n}] {title}\n{'='*66}")


def main():
    head(1, "주유소 고유 ID — 상호명으로만 붙여야 하는 문제")
    price = rd("한국석유공사_인천지역 휘발유 가격 현황_20260430 (1).csv")
    loc = rd("한국석유공사_인천지역 주유소 위치 현황_20240530.csv")
    pn = {x[0].strip() for x in price[1:]}
    ln = {x[0].strip() for x in loc[1:]}
    print(f"  인천 가격 {len(pn)}개 ↔ 인천 위치 {len(loc)-1}행"
          f"(고유 상호명 {len(ln)}개)")
    print(f"  상호명 정확일치 {len(pn & ln)}개 = {len(pn & ln)/len(pn)*100:.1f}%  "
          f"(못 붙는 곳 {len(pn - ln)}개)")

    al = rd("한국석유공사_알뜰주유소 현황_20251231.csv")
    day = [x for x in rd("과거_판매가격(주유소)20260918-20260918.csv")[1:] if len(x) > 5]
    an = {x[0].strip() for x in al[1:]}
    dn = {x[2].strip() for x in day}
    print(f"  알뜰 {len(an)}개(중복 제외, 원본 {len(al)-1}행) ↔ 일간 가격 {len(day)}개")
    print(f"  상호명 정확일치 {len(an & dn)}개 = {len(an & dn)/len(an)*100:.1f}%  "
          f"(못 붙는 곳 {len(an - dn)}개)")
    print(f"  일간 가격 파일에는 고유 ID 있음(예: {day[0][0]}), 알뜰 현황 열: {al[0]}")

    head(2, "상표 명칭 체계 불일치")
    print("  알뜰 현황 파일:", dict(collections.Counter(x[2] for x in al[1:])))
    print("  일간 가격 파일:", dict(collections.Counter(
        x[5] for x in day if "알뜰" in x[5] or "NH" in x[5])))

    head(3, "가격 파일이 스냅샷 — 데이터 행 수")
    for n in ["주유소_평균판매가격_제품별.csv", "주유소_형태별_평균판매가격.csv",
              "주유소_상표별_평균판매가격.csv", "LPG충전소_제품별_평균판매가격.csv",
              "전자상거래.csv"]:
        print(f"  {n:<48} 데이터 {len(rd(n))-1}행")
    print(f"  {'과거_판매가격(주유소)20260918-20260918.csv':<48} 주유소 {len(day)}개 "
          f"× 하루 (2행째는 기준기간 주석)")
    for n in ["한국석유공사_주유소 요소수 평균판매가격_지역별_20260630.csv",
              "한국석유공사_국내 석유비축일수_20251231.csv"]:
        print(f"  {n:<48} 데이터 {len(rd(n))-1}행  ← 시계열 있음")

    head(4, "표 구조·기간·단위 표기")
    r = rd("한국석유공사_국내 원유수입_국가별_20251231.csv")
    body = r[1:]
    cells = sum(len(x) - 1 for x in body)
    blank = sum(1 for x in body for v in x[1:] if not v.strip())
    print(f"  원유수입_국가별: {len(r[0])}열 × {len(body)}행 ({body[0][0]}~{body[-1][0]})")
    print(f"  빈 칸 {blank}/{cells} = {blank/cells*100:.1f}%")
    for n in ["LPG집단공급사업자_제품별_평균판매가격.csv",
              "LPG충전소_제품별_평균판매가격.csv",
              "LPG판매소_제품별_평균판매가격.csv"]:
        t = rd(n)
        print(f"  {n:<44} 기간표기={t[1][0]!r} 단위={t[0][1:]}")

    head(7, "LPG 3계층 가격")
    ch = rd("LPG충전소_제품별_평균판매가격.csv")
    sa = rd("LPG판매소_제품별_평균판매가격.csv")
    gr = rd("LPG집단공급사업자_제품별_평균판매가격.csv")
    for i, label in enumerate(["일반프로판", "일반부탄"], start=1):
        c, s = float(ch[1][i]), float(sa[1][i])
        print(f"  {label}: 충전소 {c:,.2f} → 판매소 {s:,.2f} 원/kg  = {s/c:.2f}배")
    print(f"  집단공급사업자: {gr[1][1]} {gr[0][1]}  ← 단위가 달라 직접 비교 불가")

    head(8, "주유소 가격차 요인 — 보통휘발유")
    f = rd("주유소_형태별_평균판매가격.csv")
    h, sf, nsf = f[0], f[1], f[2]
    gaps = sorted(((h[i], float(nsf[i]) - float(sf[i])) for i in range(2, len(h))),
                  key=lambda x: -x[1])
    print(f"  셀프 vs 비셀프 ({sf[0]}) 전국 {float(nsf[2])-float(sf[2]):.1f}원")
    print("    지역 상위:", ", ".join(f"{k} {v:.0f}원" for k, v in gaps[:3]))
    print("    지역 하위:", ", ".join(f"{k} {v:.0f}원" for k, v in gaps[-3:]))
    print(f"    최대/최소 배수: {gaps[0][1]/gaps[-1][1]:.1f}배")
    b = {x[0]: float(x[2]) for x in rd("주유소_상표별_평균판매가격.csv")[1:]}
    print(f"  알뜰(자영) {b['알뜰(자영)']:.2f} vs 정유사상표(전체) {b['정유사상표(전체)']:.2f} "
          f"= {b['정유사상표(전체)']-b['알뜰(자영)']:.1f}원")
    oils = {k: v for k, v in b.items() if k in
            ("SK에너지", "GS칼텍스", "HD현대오일뱅크", "S-OIL")}
    print(f"  정유사 상표 간 최대-최소 = {max(oils.values())-min(oils.values()):.1f}원")
    print(f"  알뜰(전체) {b['알뜰주유소(전체)']:.2f} vs 알뜰(자영) {b['알뜰(자영)']:.2f} "
          f"= {b['알뜰주유소(전체)']-b['알뜰(자영)']:.1f}원")

    head(9, "요소수 지역 격차")
    u = rd("한국석유공사_주유소 요소수 평균판매가격_지역별_20260630.csv")
    hd, last = u[0], u[-1]
    vals = sorted(((hd[i], float(last[i])) for i in range(2, len(hd)) if last[i]),
                  key=lambda x: -x[1])
    print(f"  기간 {u[1][0]} ~ {last[0]} ({len(u)-1}개월)")
    print(f"  최고 {vals[0][0]} {vals[0][1]:,.2f} / 최저 {vals[-1][0]} {vals[-1][1]:,.2f}")
    print(f"  격차 {vals[0][1]-vals[-1][1]:,.0f}원 = {vals[0][1]/vals[-1][1]:.2f}배")

    head(10, "에너지 안보")
    d = rd("한국석유공사_국내 석유비축일수_20251231.csv")
    print(f"  {d[0]}")
    print(f"  {d[1][0]}년 {d[1][1]}일 / {d[1][2]}백만배럴  →  "
          f"{d[-1][0]}년 {d[-1][1]}일 / {d[-1][2]}백만배럴  ({len(d)-1}개 연도)")


if __name__ == "__main__":
    main()
