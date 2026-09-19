# 유니스타(油NISTAR) — 한국석유공사 AI·데이터 서포터즈

2026년 한국석유공사 AI·데이터 서포터즈 활동 저장소.
Mission 1(공공데이터 모니터링) 수행에 쓰인 원본 데이터, 점검 스크립트, 증빙을 관리한다.

## 폴더 구조

```
data/raw/         공공데이터포털에서 받은 원본 파일 (수정 금지)
data/processed/   GDQ 진단 후 개선한 파일
evidence/         증빙 — 캡처, API 응답 로그, GDQ 결과
scripts/          API 호출·점검 스크립트
docs/             보고서 초안, 메모
```

## 준비

```bash
pip install -r requirements.txt
cp .env.example .env     # 그 다음 .env 를 열어 본인 인증키를 넣는다
```

> `.env` 는 `.gitignore` 에 등록되어 있어 깃허브에 올라가지 않는다.
> 인증키를 코드나 노트북에 직접 적지 말 것.

## 사용

```bash
# 전국 평균가격 조회
python scripts/opinet.py avgAllPrice

# 파라미터를 붙여 호출
python scripts/opinet.py pollAvgRecentPrice prodcd=B027

# 자동차부탄 제품코드(K015/K105) 실태 검증 → evidence/ 에 결과 저장
python scripts/check_prodcd.py
```

## 파일명 규칙

`[활동유형번호]_[담당자]_[데이터명]_[YYYYMMDD]`

예: `01_종진_지역코드API_20260922.png`

## 담당

| 담당 | 활동유형 |
| --- | --- |
| 최인영 | ④ 공공데이터 개선·활용 아이디어 / 문서 총괄 |
| 박종진 | ① 공공데이터포털 개방데이터 오류 점검 |
| 박상혁 | ② GDQ 활용 파일 품질점검·개선 |
