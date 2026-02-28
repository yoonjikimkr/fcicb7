import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

def scrape_yes24_it():
    base_url = "https://www.yes24.com/product/category/BestSellerContents"
    params = {
        "categoryNumber": "001001003",
        "sumGb": "06",
        "sex": "A",
        "age": "255",
        "goodsTp": "0",
        "addOptionTp": "0",
        "excludeTp": "2",
        "pageSize": "120",
        "goodsStatGb": "06",
        "eBookTp": "0",
        "bestType": "YES24_BESTSELLER",
        "type": "",
        "saleYear": "0",
        "saleMonth": "0",
        "weekNo": "0",
        "saleDts": "",
        "viewMode": "",
        "freeYn": ""
    }

    all_books = []
    page = 1
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "https://www.yes24.com/Product/Category/BestSeller?CategoryNumber=001001003"
    }

    while True:
        print(f"Scraping page {page}...")
        params["pageNumber"] = page
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".itemUnit")
        
        if not items:
            print("No more items found. Ending crawl.")
            break
            
        page_items_count = 0
        for item in items:
            try:
                # Rank
                rank_tag = item.select_one(".ico.rank")
                rank = rank_tag.text.strip() if rank_tag else ""
                
                # Title
                title_tag = item.select_one(".gd_name")
                title = title_tag.text.strip() if title_tag else ""
                
                # Subtitle (Secondary title)
                subtitle_tag = item.select_one(".gd_nameE")
                subtitle = subtitle_tag.text.strip() if subtitle_tag else ""
                
                # Author, Publisher, Date
                info_row = item.select_one(".info_pubGrp")
                author = ""
                publisher = ""
                pub_date = ""
                if info_row:
                    auth_tag = info_row.select_one(".info_auth")
                    author = auth_tag.text.strip() if auth_tag else ""
                    if author.endswith(" 저"):
                         author = author[:-2].strip()
                    elif author.endswith(" 지음"):
                         author = author[:-3].strip()
                    
                    pub_tag = info_row.select_one(".info_pub")
                    publisher = pub_tag.text.strip() if pub_tag else ""
                    
                    date_tag = info_row.select_one(".info_date")
                    pub_date = date_tag.text.strip() if date_tag else ""

                # Price
                price_row = item.select_one(".info_price")
                sale_price = ""
                original_price = ""
                if price_row:
                    sale_tag = price_row.select_one(".txt_num .yes_b")
                    sale_price = sale_tag.text.strip().replace(",", "") if sale_tag else ""
                    
                    orig_tag = price_row.select_one(".txt_num.dash .yes_m")
                    original_price = orig_tag.text.strip().replace(",", "") if orig_tag else ""
                
                # Sale Index
                sale_idx_tag = item.select_one(".saleNum")
                sale_index = ""
                if sale_idx_tag:
                    sale_index = sale_idx_tag.text.replace("판매지수", "").strip().replace(",", "")
                
                # Rating
                rating_tag = item.select_one(".rating_grade .yes_b")
                rating = rating_tag.text.strip() if rating_tag else ""
                
                # Review Count
                review_tag = item.select_one(".rating_rvCount .txC_blue")
                review_count = review_tag.text.strip().replace(",", "") if review_tag else "0"

                all_books.append({
                    "순위": rank,
                    "제목": title,
                    "부제목": subtitle,
                    "저자": author,
                    "출판사": publisher,
                    "출판일": pub_date,
                    "판매가": sale_price,
                    "정가": original_price,
                    "판매지수": sale_index,
                    "평점": rating,
                    "리뷰수": review_count
                })
                page_items_count += 1
            except Exception as e:
                print(f"Error parsing an item: {e}")
                continue
        
        print(f"Collected {page_items_count} items from page {page}.")
        
        # If we got fewer than 120 items, it might be the last page (though Yes24 might just stop returning items)
        # But looking at the items count is safer.
        if page_items_count < 120:
            print("Last page reached.")
            break

        # Random sleep between 0.1 and 1.0 second
        sleep_time = random.uniform(0.1, 1.0)
        time.sleep(sleep_time)
        
        page += 1

    if all_books:
        df = pd.DataFrame(all_books)
        os.makedirs("yes24it/data", exist_ok=True)
        filename = "yes24it/data/yes24_it_bestsellers.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(all_books)} books to {filename}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    scrape_yes24_it()
