"""
파일명 NFD → NFC 정규화.

한글 파일명이 자모 분리(NFD)로 저장되면 윈도우·깃허브에서 깨져 보인다.
data/raw 안의 파일명을 조합형(NFC)으로 정규화한다. 파일 내용은 건드리지 않고
이름만 바꾼다.

기본은 미리보기(변경될 목록만 출력). 실제 적용은 --apply 를 붙인다.

사용법:
  python scripts/normalize_names.py            # 미리보기
  python scripts/normalize_names.py --apply     # 실제 rename
  python scripts/normalize_names.py --apply --all   # data/ 전체 재귀

적용 후에는  git add -A  로 변경(이름)을 스테이징하면 된다.
"""
import os
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def targets(base, recursive):
    """정규화가 필요한 (원본경로, NFC경로) 쌍을 돌려준다."""
    pairs = []
    walker = os.walk(base) if recursive else [(str(base), [], os.listdir(base))]
    for dirpath, _dirs, names in walker:
        for name in names:
            if name == ".gitkeep":
                continue
            nfc = unicodedata.normalize("NFC", name)
            if nfc != name:
                pairs.append((Path(dirpath) / name, Path(dirpath) / nfc))
    return sorted(pairs)


def main():
    apply = "--apply" in sys.argv
    recursive = "--all" in sys.argv
    base = ROOT / "data" if recursive else ROOT / "data" / "raw"

    pairs = targets(base, recursive)
    if not pairs:
        print("정규화할 파일 없음 — 모두 NFC 상태입니다.")
        return

    print(f"NFC 정규화 대상: {len(pairs)}개  (base={base.relative_to(ROOT)})\n")
    for src, dst in pairs:
        print(f"  {src.name}")

    if not apply:
        print(f"\n[미리보기] 실제로 바꾸려면 --apply 를 붙이세요.")
        return

    done = 0
    for src, dst in pairs:
        if dst.exists() and not src.samefile(dst):
            print(f"[건너뜀] 이미 존재: {dst.name}")
            continue
        os.rename(src, dst)
        done += 1
    print(f"\n완료: {done}개 정규화.  다음: git add -A 로 스테이징하세요.")


if __name__ == "__main__":
    main()
