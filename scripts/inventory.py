"""
Mission 1 ② 증빙용 — data/raw 원본 파일 인벤토리 점검.

업로드한 공공데이터 원본 파일 각각에 대해
  · 인코딩          : CP949 / UTF-8 / UTF-8-BOM
  · 파일명 정규화    : NFC 여부 (NFD 자모 분리 = 윈도우·깃허브에서 깨짐)
  · 크기 / 확장자
  · 중복 다운로드 의심 : 파일명에 (1),(2) 포함
을 조사해 표로 정리한다. 파일 내용은 읽되 수정하지 않는다.

사용법:  python scripts/inventory.py
결과는 evidence/inventory_<날짜>.csv 와 .md 로 저장된다(증빙 첨부용).
"""
import csv
import os
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def detect_encoding(path):
    """파일 앞부분을 읽어 인코딩을 판별한다."""
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return "UTF-8-BOM"
    for enc in ("utf-8", "cp949"):
        try:
            data.decode(enc)
            return "UTF-8" if enc == "utf-8" else "CP949"
        except UnicodeDecodeError:
            continue
    return "UNKNOWN"


def scan():
    rows = []
    for name in sorted(os.listdir(RAW)):
        path = RAW / name
        if not path.is_file() or name == ".gitkeep":
            continue
        ext = path.suffix.lower()
        is_nfc = unicodedata.is_normalized("NFC", name)
        # 텍스트 계열만 인코딩 판별(csv). 그 외는 바이너리로 표기.
        if ext == ".csv":
            enc = detect_encoding(path)
        else:
            enc = f"(binary {ext})"
        rows.append({
            "파일명": name,
            "확장자": ext or "(없음)",
            "인코딩": enc,
            "파일명NFC": "OK" if is_nfc else "NFD(정규화필요)",
            "크기(bytes)": path.stat().st_size,
            "중복의심": "Y" if ("(1)" in name or "(2)" in name) else "",
        })
    return rows


def summarize(rows):
    from collections import Counter
    enc = Counter(r["인코딩"] for r in rows if r["확장자"] == ".csv")
    nfd = sum(1 for r in rows if r["파일명NFC"] != "OK")
    dup = sum(1 for r in rows if r["중복의심"] == "Y")
    ext = Counter(r["확장자"] for r in rows)
    lines = [
        f"- 총 파일 수: {len(rows)}",
        f"- 확장자 분포: {dict(ext)}",
        f"- CSV 인코딩: {dict(enc)}",
        f"- 파일명 NFD(정규화 필요): {nfd} / {len(rows)}",
        f"- 중복 다운로드 의심: {dup}",
    ]
    return lines


def main():
    if not RAW.exists():
        raise SystemExit(f"[오류] {RAW} 가 없습니다.")
    rows = scan()
    stamp = datetime.now().strftime("%Y%m%d")
    fields = ["파일명", "확장자", "인코딩", "파일명NFC", "크기(bytes)", "중복의심"]

    csv_out = ROOT / "evidence" / f"inventory_{stamp}.csv"
    with csv_out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize(rows)
    md_out = ROOT / "evidence" / f"inventory_{stamp}.md"
    md_lines = [
        f"# data/raw 인벤토리 점검 — {datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## 요약",
        *summary,
        "",
        "## 전체 목록",
        "",
        "| " + " | ".join(fields) + " |",
        "|" + "|".join(["---"] * len(fields)) + "|",
    ]
    for r in rows:
        md_lines.append("| " + " | ".join(str(r[f]) for f in fields) + " |")
    md_out.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("\n".join(summary))
    print(f"\n증빙 저장:\n  {csv_out.relative_to(ROOT)}\n  {md_out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
