import os
import sqlite3
import random
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")

EXTRACT_PDP_JS = """
() => {
    let subcategory = "";
    let ingredient_snippet = "";
    let badges = [];
    let list_price = 0;

    try {
        // 1. Subcategory (Breadcrumbs)
        const breadcrumbs = Array.from(document.querySelectorAll('#breadCrumbs a, .breadcrumbs a')).map(a => a.innerText.trim());
        if (breadcrumbs.length > 0) {
            subcategory = breadcrumbs.join(' > ');
        }

        // 2. Ingredient Snippet (Supplement facts or description)
        const suppFacts = document.querySelector('.supplement-facts-container, .supplement-facts, #supplement-facts');
        if (suppFacts) {
            ingredient_snippet = suppFacts.innerText.replace(/\\n+/g, ' | ').substring(0, 1000);
        } else {
            const ingredientsSection = Array.from(document.querySelectorAll('.row.item')).find(el => el.innerText.toLowerCase().includes('ingredient'));
            if (ingredientsSection) ingredient_snippet = ingredientsSection.innerText.replace(/\\n+/g, ' | ').substring(0, 1000);
        }

        // 3. Badges (Icons / Claims)
        const badgeElements = document.querySelectorAll('.product-badges img, .badge-container img, .product-claims li');
        badgeElements.forEach(el => {
            const title = el.getAttribute('title') || el.getAttribute('alt') || el.innerText;
            if (title && !badges.includes(title)) badges.push(title.trim());
        });

        // 4. List Price (MSRP / original price before discount)
        const strikePriceEl = document.querySelector('.price.strike, s, del, .pricing-list-price');
        if (strikePriceEl) {
            const num = strikePriceEl.innerText.replace(/[^0-9]/g, '');
            if (num) list_price = parseInt(num);
        }

    } catch (e) {
        console.error(e);
    }

    return {
        subcategory: subcategory,
        ingredient_snippet: ingredient_snippet,
        badges: badges.join(', '),
        list_price_krw: list_price
    };
}
"""

def scrape_top_pdps(limit=500):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 아직 수집되지 않은 (상세데이터가 비어있는) 모든 상품을 리뷰 많은 순으로 가져옵니다.
    cursor.execute('''
        SELECT product_id, product_url 
        FROM iherb_sleep_products 
        WHERE subcategory IS NULL OR subcategory = ''
        ORDER BY review_count DESC 
        LIMIT ?
    ''', (limit,))
    
    products = cursor.fetchall()
    print(f"🚀 추가로 수집할 상품: {len(products)}개 (전체 수집 목적)")

    if not products:
        print("이미 모든 상품 정보가 최신 상태입니다.")
        conn.close()
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False) 
        context = browser.new_context(
            locale="ko-KR",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()

        for idx, (pid, url) in enumerate(products, 1):
            full_url = url if url.startswith('http') else f"https://kr.iherb.com{url}"
            print(f"[{idx}/{len(products)}] 방문 중: {full_url}")
            
            retry_count = 0
            while retry_count < 3:
                try:
                    page.goto(full_url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(2500)
                    
                    # ⚠️ 본인 확인(Cloudflare) 감지 로직
                    content = page.content().lower()
                    if "verify you are " in content or "press and hold" in content or "cloudflare" in content:
                        print("🤖 보안 확인 감지! 해결을 시도합니다...")
                        page.wait_for_timeout(3000)
                        target = page.locator("iframe[src*='challenges'], #turnstile-wrapper").first
                        if target.is_visible():
                            box = target.bounding_box()
                            if box:
                                page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2, steps=10)
                                page.mouse.down()
                                page.wait_for_timeout(random.randint(4000, 5500))
                                page.mouse.up()
                                page.wait_for_timeout(2000)
                        
                        if any(x in page.content().lower() for x in ["verify you are", "press and hold"]):
                            print("👉 여전히 보안 확인이 떠 있습니다. 수동으로 해결 혹은 10초 대기...")
                            page.wait_for_timeout(10000)

                    # 데이터 추출
                    data = page.evaluate(EXTRACT_PDP_JS)
                    
                    if not data['subcategory'] and not data['ingredient_snippet']:
                        # 가끔 iHerb가 빈 페이지를 보여줄 수 있음
                        print("  ⚠ 데이터가 비어있음, 스크롤 후 재시도...")
                        page.mouse.wheel(0, 500)
                        page.wait_for_timeout(2000)
                        data = page.evaluate(EXTRACT_PDP_JS)

                    # DB 업데이트
                    cursor.execute('''
                        UPDATE iherb_sleep_products 
                        SET subcategory = ?, ingredient_snippet = ?, badges = ?, list_price_krw = ?
                        WHERE product_id = ?
                    ''', (data['subcategory'], data['ingredient_snippet'], data['badges'], data['list_price_krw'], pid))
                    conn.commit()
                    break
                    
                except Exception as e:
                    retry_count += 1
                    print(f"  ❌ 에러 발생 (재시도 {retry_count}): {e}")
                    page.wait_for_timeout(3000)
            
            # Anti-bot 랜덤 지연
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

        browser.close()
    conn.close()
    print("\n🎉 모든 수집이 완료되었습니다!")

if __name__ == "__main__":
    # 전체 432개 제품을 모두 처리하기 위해 리밋 확장
    scrape_top_pdps(500)
