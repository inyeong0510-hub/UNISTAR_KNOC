"""
Mission 1 ② 개선 실적용 — 개방 CSV 인코딩 통일(CP949 → UTF-8 BOM).

개방된 CSV 73개가 CP949 67개 / UTF-8(BOM) 6개 로 갈려 있어, 같은 기관 데이터를
한 번에 읽으면 한글이 깨진다. 원본(`data/raw/`)은 그대로 두고, 인코딩을
UTF-8(BOM)로 통일한 사본을 `data/processed/` 에 만든다.

BOM 을 붙이는 이유: 엑셀이 BOM 없는 UTF-8 CSV 를 CP949 로 잘못 읽는다.
이미 UTF-8(BOM)인 6개는 바이트 그대로 복사해 processed 쪽이 한 세트가 되게 한다.

변환 후 반드시 원본과 같은 글자인지 검증한다(디코드한 문자열 비교).
줄바꿈은 원본 바이트를 유지한다(newline="" 로 열고 텍스트를 그대로 씀).

기본은 미리보기. 실제 생성은 --apply 를 붙인다.

사용법:
  python scripts/convert_encoding.py           # 미리보기
  python scripts/convert_encoding.py --apply    # data/processed/ 에 사본 생성
"""
import csv
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
BOM = b"\xef\xbb\xbf"


def detect(data):
    """inventory.py 와 같은 판별 규칙."""
    if data.startswith(BOM):
        return "UTF-8-BOM"
    for enc in ("utf-8", "cp949"):
        try:
            data.decode(enc)
            return "UTF-8" if enc == "utf-8" else "CP949"
        except UnicodeDecodeError:
            continue
    return "UNKNOWN"


def decode(data, enc):
    if enc == "UTF-8-BOM":
        return data[len(BOM):].decode("utf-8")
    if enc == "UTF-8":
        return data.decode("utf-8")
    if enc == "CP949":
        return data.decode("cp949")
    raise ValueError("인코딩 판별 실패")


def plan():
    rows = []
    for path in sorted(RAW.glob("*.csv")):
        data = path.read_bytes()
        enc = detect(data)
        rows.append({
            "파일명": unicodedata.normalize("NFC", path.name),
            "원본인코딩": enc,
            "처리": "변환" if enc in ("CP949", "UTF-8") else
                    "복사(이미 UTF-8 BOM)" if enc == "UTF-8-BOM" else "건너뜀(판별실패)",
            "원본크기": len(data),
            "변환크기": "",
            "검증": "",
            "_path": path,
            "_enc": enc,
        })
    return rows


def run(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    for r in rows:
        path, enc = r["_path"], r["_enc"]
        if enc == "UNKNOWN":
            continue
        data = path.read_bytes()
        text = decode(data, enc)
        dst = OUT / r["파일명"]
        dst.write_bytes(BOM + text.encode("utf-8"))

        # 검증: 다시 읽어 원본과 같은 글자인지, 행·열 수가 같은지 확인
        back = decode(dst.read_bytes(), "UTF-8-BOM")
        same_text = back == text
        with path.open(encoding="cp949" if enc == "CP949" else "utf-8-sig",
                       newline="") as fh:
            src_rows = list(csv.reader(fh))
        with dst.open(encoding="utf-8-sig", newline="") as fh:
            dst_rows = list(csv.reader(fh))
        same_shape = [len(x) for x in src_rows] == [len(x) for x in dst_rows]

        r["변환크기"] = dst.stat().st_size
        r["검증"] = "OK" if (same_text and same_shape) else (
            f"불일치(text={same_text}, shape={same_shape})")
    return rows


def main():
    apply = "--apply" in sys.argv
    rows = plan()
    enc_count = Counter(r["원본인코딩"] for r in rows)
    print(f"대상 CSV {len(rows)}개 — 인코딩 분포: {dict(enc_count)}")
    print(f"변환 대상(CP949/BOM없는 UTF-8): "
          f"{enc_count['CP949'] + enc_count['UTF-8']}개, "
          f"그대로 복사: {enc_count['UTF-8-BOM']}개")

    if not apply:
        print("\n[미리보기] 실제로 만들려면 --apply 를 붙이세요. "
              f"출력 위치: {OUT.relative_to(ROOT)}/")
        return

    rows = run(rows)
    bad = [r for r in rows if r["검증"] not in ("OK", "")]
    print(f"\n생성 완료: {sum(1 for r in rows if r['검증'] == 'OK')}개 → "
          f"{OUT.relative_to(ROOT)}/")
    print(f"검증 실패: {len(bad)}개" + (f" — {[r['파일명'] for r in bad]}" if bad else ""))

    fields = ["파일명", "원본인코딩", "처리", "원본크기", "변환크기", "검증"]
    stamp = datetime.now().strftime("%Y%m%d")
    csv_out = ROOT / "evidence" / f"encoding_convert_{stamp}.csv"
    with csv_out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows([{k: r[k] for k in fields} for r in rows])

    md = [
        f"# CSV 인코딩 통일 (CP949 → UTF-8 BOM) — {datetime.now():%Y-%m-%d %H:%M}",
        "",
        f"원본 `data/raw/` 보존, 사본 `data/processed/` 생성. 스크립트: `scripts/convert_encoding.py`",
        "",
        "## 요약",
        f"- 대상 CSV: {len(rows)}개 — 원본 인코딩 {dict(enc_count)}",
        f"- CP949 → UTF-8(BOM) 변환: {enc_count['CP949']}개",
        f"- 이미 UTF-8(BOM)이라 바이트 그대로 복사: {enc_count['UTF-8-BOM']}개",
        f"- 변환 후 검증(문자열 동일 + 행·열 수 동일) 통과: "
        f"{sum(1 for r in rows if r['검증'] == 'OK')}개 / 실패 {len(bad)}개",
        "",
        "## 전체 목록",
        "",
        "| " + " | ".join(fields) + " |",
        "|" + "|".join(["---"] * len(fields)) + "|",
    ]
    for r in rows:
        md.append("| " + " | ".join(str(r[f]) for f in fields) + " |")
    md_out = ROOT / "evidence" / f"encoding_convert_{stamp}.md"
    md_out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n증빙 저장:\n  {csv_out.relative_to(ROOT)}\n  {md_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
