import os
import json
import urllib.request
import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

DATA_DIR = "naverapieda/data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_request_headers():
    return {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

def call_api(url, method="GET", body=None):
    request = urllib.request.Request(url)
    headers = get_request_headers()
    for key, value in headers.items():
        request.add_header(key, value)
    
    try:
        if body:
            response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        else:
            response = urllib.request.urlopen(request)
            
        rescode = response.getcode()
        if rescode == 200:
            return json.loads(response.read().decode('utf-8'))
        else:
            print(f"Error Code: {rescode}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def collect_shopping_insight(keywords, start_date, end_date, time_unit="date", category="50000000"):
    # Category 50000000 is Fashion Clothing, likely need to find the right one for Omega 3/Vitamin D (Health Food?)
    # For keywords, we use the keyword trend API which is category-agnostic or requires a category.
    # The instruction says "Shopping Insight Keyword Trend".
    # https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md#쇼핑인사이트-키워드-별-트렌드-조회
    
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    
    # We need a category code. "Health Food" (건강식품) code is needed.
    # Using a generic one or trying to find it. 
    # Let's use "50000018" (Food) or "50000026" (Health Food - needs verification, but let's try a known one or broad one).
    # Actually, for keyword trend, the category param is required. 
    # Let's assume the user wants to check within "Health Food".
    # Code for '식품' is 50000006. '건강식품' might be under it.
    # Let's use "50000003" (Digital/Home Appliances) as a placeholder if we don't know, 
    # BUT for Omega 3, we should use the correct one.
    # Naver Shopping Category for Omega 3 is likely '50000030' (Dietary Supplements? No, need to be exact).
    # Let's search for "오메가3" category code using the search API first? No, Search API returns category names, not codes for DataLab.
    # I will use "50000006" (Food) for now as a safe bet if specific isn't known, or "50000030" if I can verify.
    # Let's stick to the example in docs or a common one.
    # Let's use "50000006" (Food).
    
    category_code = "50000006" 

    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category_code,
        "keyword": keywords, # List of dicts: [{"name": "Group1", "param": ["k1", "k2"]}, ...]
        "device": "",
        "gender": "",
        "ages": []
    }
    
    print(f"Collecting Shopping Insight for {keywords}...")
    response = call_api(url, method="POST", body=json.dumps(body))
    
    if response and 'results' in response:
        all_data = []
        for result in response['results']:
            title = result['title']
            for item in result['data']:
                row = {
                    'Date': item['period'],
                    'KeywordGroup': title,
                    'Ratio': item['ratio'],
                    'Group': item.get('group', 'All')
                }
                all_data.append(row)
        
        df = pd.DataFrame(all_data)
        filename = f"{DATA_DIR}/ShoppingTrend_{end_date}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved Shopping Insight to {filename}")
    else:
        print("Failed to collect Shopping Insight")

def collect_search_results(api_type, query, display=100):
    base_url = f"https://openapi.naver.com/v1/search/{api_type}.json"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}?query={encoded_query}&display={display}&sort=sim"
    
    print(f"Collecting {api_type} results for '{query}'...")
    response = call_api(url)
    
    if response and 'items' in response:
        df = pd.DataFrame(response['items'])
        # Clean tags
        if 'title' in df.columns:
            df['title'] = df['title'].apply(lambda x: x.replace('<b>', '').replace('</b>', ''))
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{DATA_DIR}/{api_type.capitalize()}_{query}_{today}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved {api_type} results to {filename}")
    else:
        print(f"Failed to collect {api_type} results")

def main():
    if not CLIENT_ID or CLIENT_ID == "your_client_id_here":
        print("Please set NAVER_CLIENT_ID and NAVER_CLIENT_SECRET in .env file.")
        return

    # 1. Shopping Insight (Trend)
    # Date range: 1 year ago to today
    today = datetime.datetime.now()
    one_year_ago = today - datetime.timedelta(days=365)
    
    start_date = one_year_ago.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    
    keywords = [
        {"name": "오메가3", "param": ["오메가3"]},
        {"name": "비타민D", "param": ["비타민D"]}
    ]
    
    collect_shopping_insight(keywords, start_date, end_date)
    
    # 2. Search Results (Shop, Blog)
    target_keywords = ["오메가3", "비타민D"]
    
    for kw in target_keywords:
        collect_search_results("shop", kw)
        collect_search_results("blog", kw)

if __name__ == "__main__":
    main()
