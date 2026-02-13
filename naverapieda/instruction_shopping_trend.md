# 네이버 쇼핑 트렌드 및 데이터 수집 작업지시서

본 문서는 네이버 DataLab 및 Search API를 활용하여 특정 키워드에 대한 쇼핑 트렌드와 관련 데이터를 수집하기 위한 작업 계획서입니다.

## 1. 프로젝트 개요
- **목표**: '오메가3', '비타민D' 등 건강기능식품 관련 키워드의 최근 1년간 쇼핑 클릭 트렌드를 파악하고, 관련 블로그 포스트 및 쇼핑 상품 정보를 수집하여 기초 데이터를 확보합니다.
- **대상 키워드**: 오메가3, 비타민D (추후 확장 가능)
- **수집 기간**: 최근 1년 (실행 시점 기준)

## 2. 디렉토리 구조 및 파일 관리
작업 결과물은 `naverapieda` 폴더 내에 다음과 같이 구성합니다.

```
naverapieda/
├── docs/                 # API 문서 저장소
├── data/                 # 수집된 데이터 저장소 (CSV)
│   └── [수집내용]_[YYYYMMDD].csv
├── .env                  # API Key 관리 (Client ID, Secret)
├── main.py               # 데이터 수집 실행 스크립트
├── requirements.txt      # 파이썬 의존성 목록
└── instruction_shopping_trend.md # 본 작업지시서
```

- **데이터 파일 명명 규칙**: `[내용]_[수집날짜].csv` (예: `ShoppingTrend_Omega3_20231027.csv`)
- **보안**: `client_id`와 `client_secret`은 반드시 `.env` 파일에 저장하여 관리하며, 코드 내에 하드코딩하지 않습니다.

## 3. 데이터 수집 상세 계획

### A. 쇼핑 트렌드 수집 (Shopping Insight API)
- **API**: `POST https://openapi.naver.com/v1/datalab/shopping/category/keywords`
- **목적**: 키워드별 일간/주간/월간 클릭 추이 확인 (상대값 0~100)
- **파라미터**:
    - `startDate`, `endDate`: 최근 1년
    - `timeUnit`: `date` (일간)
    - `category`: 해당 키워드가 속한 카테고리 ID (예: 식품 > 건강기능식품)
    - `keyword`: `[{"name": "오메가3", "param": ["오메가3"]}, {"name": "비타민D", "param": ["비타민D"]}]`
- **저장**: `ShoppingTrend_[Date].csv` (컬럼: Date, Keyword, Ratio)

### B. 쇼핑 상품 정보 수집 (Search API - Shop)
- **API**: `GET https://openapi.naver.com/v1/search/shop.json`
- **목적**: 현재 판매 중인 관련 상품의 가격, 쇼핑몰, 브랜드 정보 파악
- **파라미터**:
    - `query`: "오메가3", "비타민D"
    - `display`: 100 (최대)
    - `sort`: `sim` (정확도순) 또는 `date` (날짜순)
- **저장**: `ShoppingProducts_[Keyword]_[Date].csv` (컬럼: Title, Price, Mall, Brand, Category...)

### C. 블로그 포스트 수집 (Search API - Blog)
- **API**: `GET https://openapi.naver.com/v1/search/blog.json`
- **목적**: 소비자의 리뷰, 반응, 연관 키워드 파악을 위한 텍스트 데이터 확보
- **파라미터**:
    - `query`: "오메가3 추천", "비타민D 효능" 등
    - `display`: 100
- **저장**: `BlogPosts_[Keyword]_[Date].csv` (컬럼: Title, Link, Description, PostDate)

## 4. 실행 환경 및 의존성
- **Language**: Python 3.x
- **Libraries** (Install using `uv`):
    - `uv pip install -r requirements.txt`
    - `requests`: API 호출
    - `pandas`: 데이터 처리 및 CSV 저장
    - `python-dotenv`: 환경 변수 로드
- **.env 설정**:
    ```
    NAVER_CLIENT_ID=your_id
    NAVER_CLIENT_SECRET=your_secret
    ```

## 5. 추후 활용 계획
- 수집된 트렌드 데이터와 상품 데이터를 결합하여 가격 변동과 검색량의 상관관계 분석
- Streamlit을 이용한 대시보드 시각화 (Plotly 활용)

---
**주의사항**:
- API 호출 한도를 준수하십시오 (쇼핑인사이트 1,000회/일, 검색 25,000회/일).
- 개인정보가 포함된 데이터는 수집하지 않도록 주의합니다.
