import os
import sys
import urllib.request
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# 1. 환경 변수 로드 (.env 파일 활용)
env_path = os.path.join(os.path.dirname(__file__), 'naverapieda/.env')
load_dotenv(env_path)

CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("오류: .env 파일에서 API 키를 찾을 수 없습니다.")
    sys.exit(1)

# --- 1단계: 블로그 데이터 수집 (Search API) ---
print("블로그 데이터 수집 중...")
keywords = ["가성비 명절 선물", "부모님 명절 선물 브랜드"]
blog_data = []

for keyword in keywords:
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/blog.json?query={encText}&display=100"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            # 요약 텍스트에서 태그 제거
            descriptions = [item.get('description').replace('<b>', '').replace('</b>', '') for item in data.get('items', [])]
            blog_data.append({'keyword': keyword, 'descriptions': descriptions})
            print(f"- {keyword} 수집 완료")
    except Exception as e:
        print(f"에러 발생 ({keyword}): {e}")

# --- 2단계: 쇼핑 데이터랩 트렌드 분석 ---
print("\n쇼핑 트렌드 분석 중...")
url_trend = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
keyword_groups = [
    {"name": "선크림", "param": ["선크림"]},
    {"name": "톤업 선크림", "param": ["톤업 선크림"]}
]
body = {
    "startDate": "2025-01-01",
    "endDate": "2025-12-31",
    "timeUnit": "date",
    "category": "50000002", 
    "keyword": keyword_groups,
    "device": "mo",
    "gender": "f",
    "ages": ["20", "30"]
}
headers = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET,
    "Content-Type": "application/json"
}

try:
    res = requests.post(url_trend, headers=headers, json=body)
    if res.status_code == 200:
        data = res.json()
        all_trend = []
        for result in data["results"]:
            for dp in result["data"]:
                all_trend.append({"date": dp["period"], "keyword": result["title"], "ratio": dp["ratio"]})
        df_trend = pd.DataFrame(all_trend)
        df_trend['date'] = pd.to_datetime(df_trend['date'])
        
        # 트렌드 시각화
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_trend, x='date', y='ratio', hue='keyword')
        plt.title('선크림 vs 톤업 선크림 트렌드 비교 (2025)')
        plt.xticks(rotation=45)
        plt.savefig('trend_comparison.png')
        print("- 트렌드 그래프 저장 완료 (trend_comparison.png)")
except Exception as e:
    print(f"트렌드 분석 에러: {e}")

# --- 3단계: TF-IDF 키워드 분석 (Global Workflows 준수) ---
print("\nTF-IDF 키워드 추출 중...")
for entry in blog_data:
    if not entry['descriptions']: continue
    
    # TF-IDF 벡터화 (단순 띄어쓰기 기준)
    vectorizer = TfidfVectorizer(max_features=30)
    tfidf_matrix = vectorizer.fit_transform(entry['descriptions'])
    
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1
    
    # 상위 30개 정렬
    indices = np.argsort(scores)[::-1]
    top_words = [feature_names[i] for i in indices]
    top_scores = [scores[i] for i in indices]
    
    # 시각화
    plt.figure(figsize=(10, 8))
    plt.barh(top_words, top_scores, color='skyblue')
    plt.title(f"주요 키워드 (TF-IDF): {entry['keyword']}")
    plt.gca().invert_yaxis()
    plt.savefig(f"tfidf_{entry['keyword'].replace(' ', '_')}.png")
    print(f"- {entry['keyword']} 분석 결과 저장 완료")

print("\n모든 작업이 완료되었습니다.")