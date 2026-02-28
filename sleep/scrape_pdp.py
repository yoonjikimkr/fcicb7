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

def scrape_top_pdps(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get top 100 products by review count that haven't been fully scraped
    cursor.execute('''
        SELECT product_id, product_url 
        FROM iherb_sleep_products 
        ORDER BY review_count DESC 
        LIMIT ?
    ''', (limit,))
    
    products = cursor.fetchall()
    print(f"진행할 상품 수: {len(products)}개")

    if not products:
        conn.close()
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False) # Headless=False to avoid some detections, or True
        context = browser.new_context(
            locale="ko-KR",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"}
        )
        
        # Add CDP stealth tactics if needed
        page = context.new_page()

        for idx, (pid, url) in enumerate(products, 1):
            full_url = url if url.startswith('http') else f"https://kr.iherb.com{url}"
            print(f"[{idx}/{len(products)}] 방문 중: {full_url}")
            
            try:
                page.goto(full_url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(3000) # Wait for elements to load
                page.mouse.wheel(0, 1000)   # Scroll a bit
                page.wait_for_timeout(1000)
                
                # Check for Cloudflare / CAPTCHA
                if "cloudflare" in page.content().lower() or "captcha" in page.content().lower():
                    print("  ⚠️ Cloudflare/CAPTCHA 감지됨! 10초 대기...")
                    page.wait_for_timeout(10000)
                
                # Extract data via JS
                data = page.evaluate(EXTRACT_PDP_JS)
                
                print(f"  -> Subcat: {data['subcategory'][:30]}... | Badges: {data['badges'][:30]}...")
                
                # Update DB
                cursor.execute('''
                    UPDATE iherb_sleep_products 
                    SET subcategory = ?, ingredient_snippet = ?, badges = ?, list_price_krw = ?
                    WHERE product_id = ?
                ''', (data['subcategory'], data['ingredient_snippet'], data['badges'], data['list_price_krw'], pid))
                conn.commit()
                
            except Exception as e:
                print(f"  ❌ 에러 발생: {e}")
            
            # Anti-bot delay
            delay = random.uniform(3, 7)
            print(f"  ⏳ {delay:.1f}초 대기 중...")
            time.sleep(delay)

        browser.close()
    conn.close()
    print("완료되었습니다!")

if __name__ == "__main__":
    scrape_top_pdps(100)
