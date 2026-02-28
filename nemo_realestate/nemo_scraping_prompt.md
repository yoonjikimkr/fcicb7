# Nemo Real Estate Scraping Prompt

## 1) HTTP 요청 정보
- **URL**: `https://www.nemoapp.kr/api/store/search-list`
- **Method**: `GET`
- **Headers**:
    - `accept`: `application/json, text/plain, */*`
    - `referer`: `https://www.nemoapp.kr/store`
    - `user-agent`: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...`
    - `cookie`: 세션 정보 포함 (필요 시 브라우저에서 복사)

## 2) Payload 정보 (Query Parameters)
- `CompletedOnly`: `false` (거래 완료 매물 포함 여부)
- `NELat`, `NELng`, `SWLat`, `SWLng`: 지도 내 영역 좌표 (예: 강남역 인근 `37.502, 127.031` 등)
- `Zoom`: `17` (지도 확대 수준)
- `SortBy`: `29` (정렬 기준)
- `PageIndex`: `1` (페이지 번호)

## 3) Response 데이터 일부
```json
{
  "items": [
    {
      "id": "c4cb9550-3468-4ec8-bed8-af0f03cd57e3",
      "number": 919195,
      "title": " ❤️ 아정당부동산중개법인",
      "businessLargeCodeName": "휴게음식점",
      "businessMiddleCodeName": "피자점",
      "priceTypeName": "임대",
      "deposit": 20000,
      "monthlyRent": 1500,
      "premium": 80000,
      "maintenanceFee": 500,
      "floor": 1,
      "size": 66.1,
      "nearSubwayStation": "역삼역, 도보 4분",
      "previewPhotoUrl": "https://img.nemoapp.kr/article-photos/.../s.jpg"
    }
  ],
  "totalCount": 1234
}
```

## 4) 수집 확인
- `https://www.nemoapp.kr/store` 페이지에서 스크롤 시 `PageIndex`가 증가하며 새로운 매물 데이터를 성공적으로 수집하는 것을 확인했습니다.
- API 응답의 `items` 배열에 유효한 매물 데이터가 포함되어 있습니다.

## 5) SQLite DB 스키마 및 저장 로직

### SQLite Schema
```sql
CREATE TABLE IF NOT EXISTS stores (
    id TEXT PRIMARY KEY,
    store_number INTEGER,
    title TEXT,
    business_large_category TEXT,
    business_middle_category TEXT,
    price_type TEXT,
    deposit INTEGER,
    monthly_rent INTEGER,
    premium INTEGER,
    maintenance_fee INTEGER,
    floor INTEGER,
    size REAL,
    near_subway TEXT,
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 데이터 저장 스크립트 (예시)
```python
import sqlite3

def save_to_db(items):
    conn = sqlite3.connect('nemo_properties.db')
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            id TEXT PRIMARY KEY,
            store_number INTEGER,
            title TEXT,
            business_large_category TEXT,
            business_middle_category TEXT,
            price_type TEXT,
            deposit INTEGER,
            monthly_rent INTEGER,
            premium INTEGER,
            maintenance_fee INTEGER,
            floor INTEGER,
            size REAL,
            near_subway TEXT,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    for item in items:
        cursor.execute('''
            INSERT OR REPLACE INTO stores 
            (id, store_number, title, business_large_category, business_middle_category, 
             price_type, deposit, monthly_rent, premium, maintenance_fee, floor, size, near_subway, photo_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['id'], item['number'], item['title'], item['businessLargeCodeName'], 
            item['businessMiddleCodeName'], item['priceTypeName'], item['deposit'], 
            item['monthlyRent'], item['premium'], item['maintenanceFee'], 
            item['floor'], item['size'], item.get('nearSubwayStation'), item.get('previewPhotoUrl')
        ))
    
    conn.commit()
    conn.close()
```
