import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re

def scrape_aladin_it():
    base_url = "https://www.aladin.co.kr/shop/wbrowse.aspx"
    params = {
        "BrowseTarget": "List",
        "ViewRowsCount": "25",
        "ViewType": "Detail",
        "PublishMonth": "0",
        "SortOrder": "2",
        "Stockstatus": "1",
        "PublishDay": "84",
        "CID": "351",
        "SearchOption": ""
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "https://www.aladin.co.kr/"
    }

    all_books = []
    
    # Range up to 10 pages
    for page in range(1, 11):
        print(f"Scraping Aladin page {page}...")
        params["page"] = page
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        # Aladin items are usually in .ss_book_box
        items = soup.select(".ss_book_box")
        
        if not items:
            print(f"No items found on page {page}. Ending crawl.")
            break
            
        page_items_count = 0
        for item in items:
            try:
                # Find the info list
                info_div = item.select_one(".ss_book_list")
                if not info_div:
                    continue
                
                li_elements = info_div.select("ul > li")
                if not li_elements:
                    continue
                
                # Title often in first or second LI depending on presence of icons
                # Usually look for class 'bo3'
                title_tag = info_div.select_one("a.bo3")
                title = title_tag.text.strip() if title_tag else ""
                
                # Subtitle/Description - sibling to title_tag or in same LI
                subtitle = ""
                if title_tag and title_tag.next_sibling:
                    subtitle = title_tag.next_sibling.text.strip()
                    if subtitle.startswith("- "):
                        subtitle = subtitle[2:].strip()

                # Author, Publisher, Date - Usually the LI after title
                # We need to find the LI that contains author info
                author_li = None
                for li in li_elements:
                    if "(지은이)" in li.text or "(옮긴이)" in li.text or "|" in li.text:
                        author_li = li
                        break
                
                author = ""
                publisher = ""
                pub_date = ""
                if author_li:
                    parts = [p.strip() for p in author_li.text.split("|")]
                    if len(parts) >= 3:
                        author = parts[0]
                        publisher = parts[1]
                        pub_date = parts[2]
                    elif len(parts) == 2:
                        author = parts[0]
                        publisher = parts[1]
                
                # Prices - Usually in the LI following author or containing '원'
                price_li = None
                for li in li_elements:
                    if "원 →" in li.text:
                        price_li = li
                        break
                
                original_price = ""
                sale_price = ""
                discount_rate = ""
                if price_li:
                    text = price_li.text.replace(",", "")
                    # Regex for original price before '원 →'
                    orig_match = re.search(r"(\d+)원", text.split("→")[0])
                    if orig_match:
                        original_price = orig_match.group(1)
                    
                    # Sale price in em or ss_p2
                    sale_tag = price_li.select_one(".ss_p2 em")
                    if sale_tag:
                        sale_price = sale_tag.text.strip().replace(",", "").replace("원", "")
                    
                    # Discount rate in ss_p
                    disc_tag = price_li.select_one(".ss_p")
                    if disc_tag:
                        discount_rate = disc_tag.text.strip()

                # Rating and Sales Point
                rating_li = None
                for li in li_elements:
                    if "세일즈포인트" in li.text:
                        rating_li = li
                        break
                
                rating = ""
                review_count = ""
                sales_point = ""
                if rating_li:
                    # Rating score
                    score_tag = rating_li.select_one(".star_score")
                    if score_tag:
                        rating = score_tag.text.strip()
                    
                    # Review count - usually in brackets after score
                    rv_match = re.search(r"\((\d+)\)", rating_li.text)
                    if rv_match:
                        review_count = rv_match.group(1)
                    
                    # Sales Point
                    sp_tag = rating_li.select_one(".sales_point")
                    if sp_tag:
                        sales_point = sp_tag.text.strip().replace(",", "")

                all_books.append({
                    "제목": title,
                    "부제목": subtitle,
                    "저자": author,
                    "출판사": publisher,
                    "출판일": pub_date,
                    "정가": original_price,
                    "판매가": sale_price,
                    "할인율": discount_rate,
                    "평점": rating,
                    "리뷰수": review_count,
                    "세일즈포인트": sales_point
                })
                page_items_count += 1
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
        
        print(f"Collected {page_items_count} items from page {page}.")
        
        # Check if we should continue after page 1 (Simulation of the requirement)
        if page == 1:
            if not all_books:
                print("No data found on page 1. Stopping.")
                break
            else:
                print("Page 1 verified. Continuing to page 10.")

        # Random sleep
        time.sleep(random.uniform(0.5, 2.0))

    if all_books:
        df = pd.DataFrame(all_books)
        os.makedirs("aladin/data", exist_ok=True)
        filename = "aladin/data/aladin_it_books.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(all_books)} books to {filename}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    scrape_aladin_it()
