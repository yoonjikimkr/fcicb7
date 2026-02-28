"""
iHerb Sleep 카테고리 스크래퍼 (Playwright 기반)
- 1~10페이지를 수집하여 SQLite DB에 저장
- 봇 탐지 우회를 위한 실제 브라우저 사용
"""

import json
import os
import re
import random
import sqlite3
import time

from playwright.sync_api import sync_playwright

# ── 설정 ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")
BASE_URL = "https://kr.iherb.com/c/sleep"

# 제품 데이터 추출용 JavaScript
EXTRACT_JS = """
() => {
  const products = [];
  const cards = document.querySelectorAll('.product-cell-container .product, .product-cell-container .ga-product');
  cards.forEach(card => {
    try {
      const linkEl = card.querySelector('a.absolute-link');
      if (!linkEl) return;

      const name = linkEl.getAttribute('title') || linkEl.getAttribute('aria-label') || '';
      const href = linkEl.getAttribute('href') || '';

      let pid = '';
      const idAttr = card.getAttribute('id') || '';
      const pidMatch = idAttr.match(/pid_(\\d+)/);
      if (pidMatch) pid = pidMatch[1];

      const price = linkEl.getAttribute('data-ga-discount-price') || '0';

      let rating = 0;
      const ratingEl = card.querySelector('a.stars, a[class*="stars"]');
      if (ratingEl) {
        const rTitle = ratingEl.getAttribute('title') || '';
        const rm = rTitle.match(/([\\d.]+)/);
        if (rm) rating = parseFloat(rm[1]);
      }

      let reviewCount = 0;
      const reviewEl = card.querySelector('a.rating-count span, a.rating-count, .rating-count');
      if (reviewEl) {
        const rc = reviewEl.textContent.trim().replace(/,/g, '').replace(/[^\\d]/g, '');
        reviewCount = parseInt(rc) || 0;
      }

      const brand = name.includes(',') ? name.split(',')[0].trim() : '';

      products.push({
        product_id: parseInt(pid) || 0,
        product_name: name,
        brand: brand,
        product_url: href,
        price: parseInt(price) || 0,
        rating: rating,
        review_count: reviewCount,
      });
    } catch (e) {}
  });
  return products;
}
"""


def init_db() -> sqlite3.Connection:
    """SQLite DB 및 테이블 초기화"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
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
    """)
    conn.commit()
    return conn


def save_to_db(conn: sqlite3.Connection, products: list[dict], page_number: int):
    """제품 데이터를 SQLite에 저장"""
    cursor = conn.cursor()
    for p in products:
        cursor.execute(
            """
            INSERT OR REPLACE INTO iherb_sleep_products
            (product_id, product_name, brand, product_url, price, rating, review_count, page_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                p["product_id"],
                p["product_name"],
                p["brand"],
                p["product_url"],
                p["price"],
                p["rating"],
                p["review_count"],
                page_number,
            ),
        )
    conn.commit()


def scrape_pages(start: int = 1, end: int = 10):
    """Playwright로 지정 범위의 페이지를 수집하여 DB에 저장"""
    conn = init_db()
    total = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        )
        page = context.new_page()

        for pg in range(start, end + 1):
            url = f"{BASE_URL}?soa=true&p={pg}"
            print(f"📄 {pg}페이지 수집 중... ({url})")

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # 페이지 내 제품 카드가 나타날 때까지 대기
                page.wait_for_selector(".product-cell-container", timeout=15000)
                page.wait_for_timeout(2000)  # 추가 렌더링 대기
            except Exception as e:
                print(f"  ❌ 페이지 로드 실패: {e}")
                continue

            # 스크롤하여 모든 제품 로드
            for _ in range(3):
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(500)

            # JavaScript로 제품 데이터 추출
            try:
                products = page.evaluate(EXTRACT_JS)
            except Exception as e:
                print(f"  ❌ 데이터 추출 실패: {e}")
                continue

            if not products:
                print(f"  ⚠ 제품을 찾지 못했습니다")
                continue

            save_to_db(conn, products, pg)
            print(f"  ✅ {len(products)}개 제품 저장 완료")
            total += len(products)

            # 봇 탐지 우회를 위한 랜덤 지연
            if pg < end:
                delay = random.uniform(2, 4)
                print(f"  ⏳ {delay:.1f}초 대기 중...")
                time.sleep(delay)

        browser.close()

    conn.close()
    print(f"\n🎉 총 {total}개 제품 수집 완료! → {DB_PATH}")

    # 수집 결과 확인
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM iherb_sleep_products")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM iherb_sleep_products LIMIT 3")
    samples = cursor.fetchall()
    conn.close()

    print(f"\n📊 DB 내 총 제품 수: {count}")
    print("📋 샘플 데이터:")
    for s in samples:
        print(f"  - [{s[1]}] {s[2]} | ₩{s[5]:,} | ⭐{s[6]} | 리뷰 {s[7]:,}개")


if __name__ == "__main__":
    scrape_pages(1, 10)
