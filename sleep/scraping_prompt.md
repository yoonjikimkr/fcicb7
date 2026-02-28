# iHerb Sleep 카테고리 데이터 수집 프롬프트

이 문서에는 iHerb 수면 보조제 카테고리 데이터 수집을 위한 분석 내용이 담겨 있습니다. 모든 수집, 분석 결과는 `sleep` 폴더 하단에 생성됩니다.

## 1) HTTP 요청 정보와 헤더

- **URL**: `https://kr.iherb.com/c/sleep?soa=true&p={page}`
- **Method**: `GET`
- **Headers**:
    - `Accept`: `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8`
    - `Accept-Language`: `ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7`
    - `User-Agent`: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36`
    - `Referer`: `https://kr.iherb.com/c/sleep`
    - `Cookie`: 세션 정보 포함 (필요 시 브라우저에서 복사)

> **참고**: iHerb는 봇 탐지가 있으므로, 반드시 적절한 `User-Agent`와 `Accept-Language: ko-KR` 헤더를 포함해야 합니다. 403 에러 발생 시 브라우저 쿠키를 함께 전송해야 할 수 있습니다.

## 2) Payload 정보 (URL Parameters)

GET 요청이므로 별도 Body 없이 URL 파라미터로 필터링/페이지네이션 수행:

| 파라미터 | 값 | 설명 |
|---------|------|------|
| `soa` | `true` | "Ships on its Own" 필터 (단독 배송 가능 제품) |
| `p` | `1` ~ `10` | 페이지 번호 (1부터 시작) |

- 한 페이지당 약 **48개** 제품이 표시됩니다.
- 10페이지 수집 시 약 **480개** 제품 데이터를 확보할 수 있습니다.

## 3) Response 데이터 일부

### HTML 구조 (SSR 방식)
제품 카드는 아래와 같은 HTML 구조로 렌더링됩니다:

```html
<div class="product-cell-container">
  <div class="product-inner product-inner-wide">
    <div class="absolute-link-wrapper">
      <a href="/pr/natrol-melatonin-sleep-fast-dissolve-strawberry-5-mg-150-tablets/66643">
        Natrol, 멜라토닌 수면, 패스트 디졸브, 딸기, 5mg, 150정
      </a>
    </div>
    <div class="price">
      <span class="price-olp">₩16,168</span>
    </div>
    <div class="rating">
      <img alt="4.7 중 5 별 등급" />
      <span class="rating-count">45,878</span>
    </div>
  </div>
</div>
```

### 수집 가능한 필드
| 필드명 | 예시 값 | 설명 |
|--------|---------|------|
| `product_id` | `66643` | URL에서 추출되는 제품 고유 ID |
| `product_name` | `Natrol, 멜라토닌 수면, 패스트 디졸브, 딸기, 5mg, 150정` | 한글 제품명 |
| `brand` | `Natrol` | 브랜드명 |
| `product_url` | `https://kr.iherb.com/pr/natrol-melatonin-sleep.../66643` | 제품 상세 URL |
| `price` | `16168` | KRW 판매가 (정수) |
| `rating` | `4.7` | 평점 (5점 만점) |
| `review_count` | `45878` | 리뷰 수 |

## 4) 수집 확인

- `https://kr.iherb.com/c/sleep?soa=true&p=1` 페이지에서 약 48개의 제품 데이터가 정상적으로 표시되는 것을 확인했습니다.
- `p=1` → `p=2` → ... → `p=10` 으로 페이지 번호를 변경하면 다른 제품이 로드됩니다.
- `Accept-Language: ko-KR` 헤더를 포함해야 한글 제품명 및 KRW 가격이 반환됩니다.
- 봇 탐지를 우회하기 위해 요청 간 **1~3초** 랜덤 지연을 적용합니다.

## 5) SQLite DB 스키마 및 저장 로직

### SQLite Schema
```sql
CREATE TABLE IF NOT EXISTS iherb_sleep_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER UNIQUE,
    product_name TEXT NOT NULL,
    brand TEXT,
    product_url TEXT,
    price INTEGER,
    rating REAL,
    review_count INTEGER,
    page_number INTEGER,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 데이터 저장 스크립트 (예시)
```python
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random

# ── 설정 ──
DB_PATH = "sleep/data/iherb_sleep.db"
BASE_URL = "https://kr.iherb.com/c/sleep"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://kr.iherb.com/c/sleep",
}

def init_db():
    """SQLite DB 및 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iherb_sleep_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER UNIQUE,
            product_name TEXT NOT NULL,
            brand TEXT,
            product_url TEXT,
            price INTEGER,
            rating REAL,
            review_count INTEGER,
            page_number INTEGER,
            captured_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def parse_products(html, page_number):
    """HTML에서 제품 데이터를 파싱"""
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    for card in soup.select(".product-cell-container"):
        try:
            # 제품 링크 및 이름
            link = card.select_one("a.absolute-link-wrapper, .absolute-link-wrapper a")
            if not link:
                continue
            
            href = link.get("href", "")
            product_name = link.get_text(strip=True)
            
            # product_id 추출 (URL 끝 숫자)
            product_id = int(href.rstrip("/").split("/")[-1]) if href else None
            product_url = f"https://kr.iherb.com{href}" if href.startswith("/") else href
            
            # 브랜드 (제품명 첫 번째 콤마 앞)
            brand = product_name.split(",")[0].strip() if "," in product_name else ""
            
            # 가격
            price_el = card.select_one(".price bdi, .price .price-olp, .price")
            price_text = price_el.get_text(strip=True) if price_el else "0"
            price = int("".join(filter(str.isdigit, price_text))) if price_text else 0
            
            # 평점
            rating_img = card.select_one(".rating img, img[alt*='별']")
            rating = 0.0
            if rating_img:
                alt = rating_img.get("alt", "")
                # "4.7 중 5 별 등급" 같은 형태에서 숫자 추출
                import re
                m = re.search(r"([\d.]+)", alt)
                if m:
                    rating = float(m.group(1))
            
            # 리뷰 수
            review_el = card.select_one(".rating-count, .stars-text")
            review_count = 0
            if review_el:
                review_text = review_el.get_text(strip=True).replace(",", "")
                review_count = int("".join(filter(str.isdigit, review_text))) if review_text else 0
            
            products.append({
                "product_id": product_id,
                "product_name": product_name,
                "brand": brand,
                "product_url": product_url,
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "page_number": page_number,
            })
        except Exception as e:
            print(f"  ⚠ 파싱 오류: {e}")
            continue
    
    return products

def save_to_db(conn, products):
    """제품 데이터를 SQLite에 저장"""
    cursor = conn.cursor()
    for p in products:
        cursor.execute('''
            INSERT OR REPLACE INTO iherb_sleep_products
            (product_id, product_name, brand, product_url, price, rating, review_count, page_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p["product_id"], p["product_name"], p["brand"], p["product_url"],
            p["price"], p["rating"], p["review_count"], p["page_number"]
        ))
    conn.commit()

def scrape_pages(start=1, end=10):
    """1~10페이지를 수집하여 DB에 저장"""
    import os
    os.makedirs("sleep/data", exist_ok=True)
    
    conn = init_db()
    total = 0
    
    for page in range(start, end + 1):
        params = {"soa": "true", "p": page}
        print(f"📄 {page}페이지 수집 중...")
        
        try:
            resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ❌ 요청 실패: {e}")
            continue
        
        products = parse_products(resp.text, page)
        save_to_db(conn, products)
        
        print(f"  ✅ {len(products)}개 제품 저장 완료")
        total += len(products)
        
        # 봇 탐지 우회를 위한 랜덤 지연
        delay = random.uniform(1, 3)
        time.sleep(delay)
    
    conn.close()
    print(f"\n🎉 총 {total}개 제품 수집 완료! → {DB_PATH}")

if __name__ == "__main__":
    scrape_pages(1, 10)
```

### 실행 방법
```bash
cd /Users/kimyo/Documents/PARA/1_Project/Antigravity/fcicb7
python -m sleep.scraper
# 또는
python sleep/scraper.py
```
