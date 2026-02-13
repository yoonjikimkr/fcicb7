import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
import datetime
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Naver API Shopping Dashboard", layout="wide")

# Load Environment Variables
load_dotenv()

# Helper function to get API keys
def get_api_keys():
    # Try loading from Streamlit secrets (for Cloud)
    if "NAVER_CLIENT_ID" in st.secrets:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
    else:
        # Fallback to local .env
        client_id = os.getenv("NAVER_CLIENT_ID")
        client_secret = os.getenv("NAVER_CLIENT_SECRET")
    return client_id, client_secret

CLIENT_ID, CLIENT_SECRET = get_api_keys()

# API Headers
def get_headers(client_id, client_secret):
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json"
    }

# API Call Function
def call_api(url, headers, method="GET", body=None):
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, data=body)
        else:
            response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Request Failed: {e}")
        return None

# --- Data Collection Functions ---

@st.cache_data(ttl=3600)
def get_shopping_trend(keywords, start_date, end_date, category_code="50000000"):
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = get_headers(CLIENT_ID, CLIENT_SECRET)
    
    # Construct keyword groups
    keyword_groups = [{"name": kw, "param": [kw]} for kw in keywords]
    
    body = json.dumps({
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": category_code,
        "keyword": keyword_groups,
        "device": "",
        "gender": "",
        "ages": []
    })
    
    data = call_api(url, headers, method="POST", body=body)
    if not data or 'results' not in data:
        return pd.DataFrame()

    all_data = []
    for result in data['results']:
        title = result['title']
        for item in result['data']:
            all_data.append({
                'Date': item['period'],
                'Keyword': title,
                'Ratio': item['ratio']
            })
    return pd.DataFrame(all_data)

@st.cache_data(ttl=3600)
def get_search_results(api_type, query, display=100):
    url = "https://openapi.naver.com/v1/search/shop.json" if api_type == 'shop' else "https://openapi.naver.com/v1/search/blog.json"
    headers = get_headers(CLIENT_ID, CLIENT_SECRET)
    params = f"?query={query}&display={display}&sort=sim"
    
    data = call_api(url + params, headers)
    if not data or 'items' not in data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data['items'])
    # Clean HTML tags
    if 'title' in df.columns:
        df['title'] = df['title'].apply(lambda x: x.replace('<b>', '').replace('</b>', ''))
    if 'description' in df.columns:
        df['description'] = df['description'].apply(lambda x: x.replace('<b>', '').replace('</b>', ''))
        
    return df

# --- Sidebar ---
st.sidebar.title("Configuration")

# API Key Input (Optional override)
if not CLIENT_ID or not CLIENT_SECRET:
    st.sidebar.warning("API Keys not found in env or secrets.")
    user_client_id = st.sidebar.text_input("Naver Client ID")
    user_client_secret = st.sidebar.text_input("Naver Client Secret", type="password")
    if user_client_id and user_client_secret:
        CLIENT_ID = user_client_id
        CLIENT_SECRET = user_client_secret

# Keyword Input
keywords_input = st.sidebar.text_input("Keywords (comma separated)", "오메가3, 비타민D")
keywords = [k.strip() for k in keywords_input.split(',')]

# Date Range
today = datetime.date.today()
start_date = st.sidebar.date_input("Start Date", today - datetime.timedelta(days=365))
end_date = st.sidebar.date_input("End Date", today)

# Category Code (Optional)
category_code = st.sidebar.text_input("Category Code (Shopping Trend)", "50000000") # Fashion default, user might need to change
st.sidebar.markdown("[Find Category Code](https://developers.naver.com/docs/serviceapi/datalab/shopping/shopping.md#%EC%87%BC%ED%95%91%EC%9D%B8%EC%82%AC%EC%9D%B4%ED%8A%B8-%EB%B6%84%EC%95%BC%EB%B3%84-%ED%8A%B8%EB%A0%8C%EB%93%9C-%EC%A1%B0%ED%9A%8C)")


run_btn = st.sidebar.button("Run Analysis")

# --- Main Dashboard ---
st.title("Naver Shopping & Search Trend Dashboard")

if run_btn:
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error("Please provide valid API Keys.")
    else:
        with st.spinner("Fetching Data..."):
            # 1. Shopping Trend
            trend_df = get_shopping_trend(keywords, str(start_date), str(end_date), category_code)
            
            # 2. Search Results (Shop & Blog) for each keyword
            shop_results = {}
            blog_results = {}
            for kw in keywords:
                shop_results[kw] = get_search_results('shop', kw)
                blog_results[kw] = get_search_results('blog', kw)
            
        st.success("Data Collection Complete!")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Shopping Trend", "Product Analysis", "Blog Analysis", "Raw Data"])
        
        with tab1:
            st.header("Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Keywords", len(keywords))
            col2.metric("Date Range", f"{start_date} ~ {end_date}")
            
            # Total Products Found
            total_products = sum([len(df) for df in shop_results.values()])
            col3.metric("Total Products Scraped", total_products)
            
            # Summary Table
            summary_data = []
            for kw in keywords:
                s_df = shop_results[kw]
                b_df = blog_results[kw]
                if not s_df.empty:
                    avg_price = pd.to_numeric(s_df['lprice'], errors='coerce').mean()
                    min_price = pd.to_numeric(s_df['lprice'], errors='coerce').min()
                    max_price = pd.to_numeric(s_df['lprice'], errors='coerce').max()
                else:
                    avg_price, min_price, max_price = 0, 0, 0
                    
                summary_data.append({
                    "Keyword": kw,
                    "Avg Price": f"{avg_price:,.0f} KRW",
                    "Min Price": f"{min_price:,.0f} KRW",
                    "Max Price": f"{max_price:,.0f} KRW",
                    "Products": len(s_df),
                    "Blog Posts": len(b_df)
                })
            st.dataframe(pd.DataFrame(summary_data))

        with tab2:
            st.header("Shopping Trend (Click Ratio)")
            if not trend_df.empty:
                fig = px.line(trend_df, x='Date', y='Ratio', color='Keyword', title="Daily Click Trend")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No trend data available. Check category code or date range.")

        with tab3:
            st.header("Product Analysis")
            
            selected_kw = st.selectbox("Select Keyword for Product Analysis", keywords)
            df_shop = shop_results[selected_kw]
            
            if not df_shop.empty:
                df_shop['lprice'] = pd.to_numeric(df_shop['lprice'], errors='coerce')
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.subheader("Price Distribution")
                    fig_hist = px.histogram(df_shop, x="lprice", nbins=20, title="Price Histogram")
                    st.plotly_chart(fig_hist, use_container_width=True)
                    
                with col_b:
                    st.subheader("Top Brands")
                    if 'brand' in df_shop.columns:
                        top_brands = df_shop['brand'].value_counts().head(10)
                        fig_bar = px.bar(top_brands, x=top_brands.index, y=top_brands.values, labels={'x': 'Brand', 'y': 'Count'})
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.info("Brand info not available.")

                col_c, col_d = st.columns(2)
                
                with col_c:
                    st.subheader("Price Box Plot")
                    fig_box = px.box(df_shop, y="lprice", title="Price Range")
                    st.plotly_chart(fig_box, use_container_width=True)

                with col_d:
                    st.subheader("Mall Share")
                    if 'mallName' in df_shop.columns:
                        mall_share = df_shop['mallName'].value_counts().head(10)
                        fig_pie = px.pie(names=mall_share.index, values=mall_share.values, title="Top 10 Malls")
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                st.subheader("Product List")
                st.dataframe(df_shop[['title', 'lprice', 'mallName', 'brand', 'link']])
            else:
                st.warning("No product data found.")

        with tab4:
            st.header("Blog Analysis")
            selected_kw_blog = st.selectbox("Select Keyword for Blog Analysis", keywords, key='blog_kw')
            df_blog = blog_results[selected_kw_blog]
            
            if not df_blog.empty:
                if 'postdate' in df_blog.columns:
                    df_blog['postdate'] = pd.to_datetime(df_blog['postdate'], format='%Y%m%d')
                    daily_posts = df_blog['postdate'].value_counts().sort_index()
                    
                    st.subheader("Daily Blog Posts")
                    fig_blog_bar = px.bar(x=daily_posts.index, y=daily_posts.values, labels={'x': 'Date', 'y': 'Count'})
                    st.plotly_chart(fig_blog_bar, use_container_width=True)
                
                st.subheader("Blog Posts List")
                st.dataframe(df_blog[['title', 'postdate', 'bloggername', 'link']])
            else:
                st.warning("No blog data found.")

        with tab5:
            st.header("Raw Data Download")
            
            if not trend_df.empty:
                csv_trend = trend_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Trend CSV", csv_trend, "trend_data.csv", "text/csv")
            
            for kw in keywords:
                if not shop_results[kw].empty:
                    csv_shop = shop_results[kw].to_csv(index=False).encode('utf-8')
                    st.download_button(f"Download Shop CSV ({kw})", csv_shop, f"shop_{kw}.csv", "text/csv")
                
                if not blog_results[kw].empty:
                    csv_blog = blog_results[kw].to_csv(index=False).encode('utf-8')
                    st.download_button(f"Download Blog CSV ({kw})", csv_blog, f"blog_{kw}.csv", "text/csv")

else:
    st.info("Click 'Run Analysis' to fetch data.")
