# 쇼핑인사이트 - Datalab

## 쇼핑인사이트 개요

### 개요
쇼핑인사이트 API는 네이버 데이터랩의 쇼핑인사이트를 API로 실행할 수 있게 하는 RESTful API입니다.
네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서의 검색 클릭 추이 데이터를 JSON 형식으로 반환합니다. 쇼핑 분야의 분야별 검색 클릭 추이와 특정한 쇼핑 분야에서 검색 키워드별 검색 클릭 추이를 확인할 수 있습니다.
API를 호출할 때는 쇼핑 분야와 검색 키워드, 검색 조건을 JSON 형식의 데이터로 전달합니다.
쇼핑인사이트 API의 하루 호출 한도는 1,000회입니다.

### 쇼핑인사이트 API 특징
쇼핑인사이트 API는 비로그인 방식 오픈 API입니다.
비로그인 방식 오픈 API는 네이버 오픈API를 호출할 때 HTTP 요청 헤더에 클라이언트 아이디와 클라이언트 시크릿 값만 전송해 사용할 수 있는 오픈 API입니다.

### 사전 준비 사항
쇼핑인사이트 API를 사용하려면 먼저 네이버 개발자 센터에서 애플리케이션을 등록하고 클라이언트 아이디와 클라이언트 시크릿을 발급받아야 합니다.

## 쇼핑인사이트 API 레퍼런스

### 쇼핑인사이트 분야별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/categories`
- **Method**: POST
- **설명**: 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서의 검색 클릭 추이를 쇼핑 분야별로 조회한 데이터를 JSON 형식으로 반환합니다.

### 쇼핑인사이트 분야 내 기기별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/category/device`
- **Method**: POST
- **설명**: 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서 특정 쇼핑 분야의 검색 클릭 추이를 기기별(PC, 모바일)로 조회한 데이터를 JSON 형식으로 반환합니다.

### 쇼핑인사이트 분야 내 성별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/category/gender`
- **Method**: POST
- **설명**: 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서 특정 쇼핑 분야의 검색 클릭 추이를 사용자의 성별로 조회한 데이터를 JSON 형식으로 반환합니다.

### 쇼핑인사이트 분야 내 연령별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/category/age`
- **Method**: POST
- **설명**: 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서 특정 쇼핑 분야의 검색 클릭 추이를 사용자의 연령별로 조회한 데이터를 JSON 형식으로 반환합니다.

### 쇼핑인사이트 키워드별 트렌드 조회
- **URL**: `https://openapi.naver.com/v1/datalab/shopping/category/keywords`
- **Method**: POST
- **설명**: 네이버 통합검색의 쇼핑 영역과 네이버쇼핑에서 특정 쇼핑 분야의 검색 클릭 추이를 검색 키워드별로 조회한 데이터를 JSON 형식으로 반환합니다.

### 파라미터 (공통)
- `startDate` (string, Y): 조회 기간 시작 날짜(yyyy-mm-dd)
- `endDate` (string, Y): 조회 기간 종료 날짜(yyyy-mm-dd)
- `timeUnit` (string, Y): 구간 단위 (date, week, month)
- `category` (string/array, Y): 쇼핑 분야 코드
- `keyword` (array, Y - 키워드 조회시): 검색 키워드 그룹 및 검색어
- `device` (string, N): 기기 (pc, mo)
- `gender` (string, N): 성별 (m, f)
- `ages` (array, N): 연령 (10, 20, 30, 40, 50, 60)

### 요청 헤더
- `X-Naver-Client-Id`: {Client ID}
- `X-Naver-Client-Secret`: {Client Secret}
- `Content-Type`: `application/json`
