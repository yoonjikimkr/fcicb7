# 검색 > 쇼핑 - Search API

## 쇼핑 검색 개요
쇼핑 검색은 검색 API를 사용해 네이버 검색의 쇼핑 검색 결과를 반환하는 RESTful API입니다.
쇼핑 검색 결과를 XML 형식 또는 JSON 형식으로 반환합니다.
하루 호출 한도는 25,000회입니다.
비로그인 방식 오픈 API입니다.

## 쇼핑 검색 결과 조회

### 요청 URL
- XML: `https://openapi.naver.com/v1/search/shop.xml`
- JSON: `https://openapi.naver.com/v1/search/shop.json`

### HTTP 메서드
- `GET`

### 파라미터
- `query` (String, Y): 검색어 (UTF-8 인코딩)
- `display` (Integer, N): 검색 결과 개수 (기본 10, 최대 100)
- `start` (Integer, N): 검색 시작 위치 (기본 1, 최대 1000)
- `sort` (String, N): 정렬 방법
  - `sim`: 정확도순 (기본값)
  - `date`: 날짜순
  - `asc`: 가격 오름차순
  - `dsc`: 가격 내림차순
- `filter` (String, N): `naverpay` (네이버페이 연동 상품)
- `exclude` (String, N): 제외할 상품 유형 (`used`, `rental`, `cbshop`)

### 요청 헤더
- `X-Naver-Client-Id`: {Client ID}
- `X-Naver-Client-Secret`: {Client Secret}

### 응답 필드 (JSON Item)
- `title`: 상품 이름
- `link`: 상품 정보 URL
- `image`: 썸네일 이미지 URL
- `lprice`: 최저가
- `hprice`: 최고가
- `mallName`: 쇼핑몰 이름
- `productId`: 상품 ID
- `productType`: 상품 타입
- `maker`: 제조사
- `brand`: 브랜드
- `category1` ~ `category4`: 카테고리 정보
