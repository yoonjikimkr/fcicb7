# 네이버 오픈API 종류

네이버 오픈API는 인증 여부에 따라 **로그인 방식 오픈 API**와 **비로그인 방식 오픈 API**로 구분됩니다.

## 비로그인 방식 오픈 API
비로그인 방식 오픈 API는 HTTP 헤더에 **클라이언트 아이디**와 **클라이언트 시크릿** 값만 전송해 사용할 수 있는 오픈 API입니다. 네이버 로그인의 인증을 통한 접근 토큰을 획득할 필요가 없습니다.

### 주요 API 목록
1. **데이터랩**: 네이버 데이터랩의 검색어 트렌드와 쇼핑인사이트를 API로 실행할 수 있게 하는 API입니다.
2. **검색**: 네이버 검색 결과를 뉴스, 백과사전, 블로그, 쇼핑, 웹 문서, 전문정보, 지식iN, 책, 카페글 등 분야별로 볼 수 있는 API입니다.
3. **이미지 캡차 / 음성 캡차**: 캡차 기능을 외부 서비스에 사용할 수 있게 하는 API입니다.
4. **네이버 공유하기**: 콘텐츠를 공유할 수 있게 하는 API입니다.
5. **Clova Face Recognition**: 얼굴 인식 API.

### 데이터랩 API 엔드포인트
- `POST https://openapi.naver.com/v1/datalab/search` (통합검색어 트렌드)
- `POST https://openapi.naver.com/v1/datalab/shopping/categories` (쇼핑 분야별 트렌드)
- `POST https://openapi.naver.com/v1/datalab/shopping/category/device`
- `POST https://openapi.naver.com/v1/datalab/shopping/category/gender`
- `POST https://openapi.naver.com/v1/datalab/shopping/category/age`
- `POST https://openapi.naver.com/v1/datalab/shopping/category/keywords` (쇼핑 키워드별 트렌드)
- `POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/device`
- `POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/gender`
- `POST https://openapi.naver.com/v1/datalab/shopping/category/keyword/age`

### 검색 API 엔드포인트
- `GET https://openapi.naver.com/v1/search/news`
- `GET https://openapi.naver.com/v1/search/encyc`
- `GET https://openapi.naver.com/v1/search/blog`
- `GET https://openapi.naver.com/v1/search/shop`
- ... (기타 검색 API)
