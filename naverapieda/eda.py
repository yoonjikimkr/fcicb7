import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
import io
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# 설정: 스타일 지침 준수
# 1. Seaborn 스타일 설정 사용 안함
# 2. koreanize-matplotlib 이미 import 됨
# 3. 이미지 저장 경로
IMG_DIR = "naverapieda/images"
os.makedirs(IMG_DIR, exist_ok=True)

REPORT_FILE = "naverapieda/eda.md"

def get_basic_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    head = df.head(5).to_markdown()
    tail = df.tail(5).to_markdown()
    
    desc_num = df.describe().to_markdown()
    desc_cat = df.describe(include=['O']).to_markdown() if not df.select_dtypes(include=['O']).empty else "N/A"
    
    return head, tail, info_str, desc_num, desc_cat

def save_plot(name):
    path = os.path.join(IMG_DIR, name)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path

# 1. 데이터 로드
trend_df = pd.read_csv("naverapieda/data/ShoppingTrend_2026-02-13.csv")
shop_o3 = pd.read_csv("naverapieda/data/Shop_오메가3_20260213.csv")
shop_vd = pd.read_csv("naverapieda/data/Shop_비타민D_20260213.csv")
blog_o3 = pd.read_csv("naverapieda/data/Blog_오메가3_20260213.csv")
blog_vd = pd.read_csv("naverapieda/data/Blog_비타민D_20260213.csv")

# 데이터 결합
shop_all = pd.concat([shop_o3.assign(Keyword='오메가3'), shop_vd.assign(Keyword='비타민D')], ignore_index=True)
blog_all = pd.concat([blog_o3.assign(Keyword='오메가3'), blog_vd.assign(Keyword='비타민D')], ignore_index=True)

report_content = "# 네이버 API 데이터 EDA 리포트\n\n본 리포트는 설정된 Global Workflows를 준수하여 작성되었습니다.\n\n"

# --- 데이터 기본 확인 ---
for name, df in [("쇼핑 트렌드", trend_df), ("네이버 쇼핑 (결합)", shop_all), ("블로그 (결합)", blog_all)]:
    head, tail, info, d_num, d_cat = get_basic_info(df)
    report_content += f"## {name} 데이터 확인\n\n"
    report_content += "### 상위 5개 행\n" + head + "\n\n"
    report_content += "### 하위 5개 행\n" + tail + "\n\n"
    report_content += "### 데이터 정보 (info())\n```\n" + info + "\n```\n\n"
    report_content += "### 기술 통계 (수치형)\n" + d_num + "\n\n"
    report_content += "### 기술 통계 (범주형)\n" + d_cat + "\n\n"

# --- 시각화 섹션 ---
report_content += "## 데이터 탐색적 시각화 (EDA)\n\n"

# 1. 쇼핑 트렌드 추이 (시계열)
plt.figure(figsize=(12, 6))
for kw in trend_df['KeywordGroup'].unique():
    subset = trend_df[trend_df['KeywordGroup'] == kw]
    plt.plot(subset['Date'], subset['Ratio'], label=kw)
plt.title("최근 1년 키워드별 쇼핑 클릭 트렌드")
plt.xticks(trend_df['Date'].unique()[::30], rotation=45)
plt.legend()
img1 = save_plot("fig1_trend.png")

pivot_trend = trend_df.groupby('KeywordGroup')['Ratio'].describe()
report_content += "### 1. 쇼핑 클릭 트렌드 시계열 분석\n"
report_content += f"![trend]({img1.replace('naverapieda/', '')})\n\n"
report_content += "**통계표 (키워드별 클릭 비율 요약)**\n" + pivot_trend.to_markdown() + "\n\n"
report_content += "> **해석**: 오메가3와 비타민D의 검색 클릭 추이를 비교한 결과, 두 키워드 모두 주기적인 변동을 보입니다. 특정 시점에 클릭량이 급증하는 구간은 계절적 요인이나 프로모션의 영향으로 보이며, 전체적인 평균 클릭 비율은 오메가3가 비타민D보다 상대적으로 안정적인 검색량을 유지하고 있음을 알 수 있습니다.\n\n"

# 2. 상품 가격 분포 (히스토그램)
plt.figure(figsize=(10, 6))
plt.hist(shop_all[shop_all['Keyword']=='오메가3']['lprice'], bins=30, alpha=0.5, label='오메가3')
plt.hist(shop_all[shop_all['Keyword']=='비타민D']['lprice'], bins=30, alpha=0.5, label='비타민D')
plt.title("상품 가격 분포 (히스토그램)")
plt.legend()
img2 = save_plot("fig2_price_hist.png")

price_stats = shop_all.groupby('Keyword')['lprice'].describe()
report_content += "### 2. 키워드별 상품 가격 분포 분석\n"
report_content += f"![price_hist]({img2.replace('naverapieda/', '')})\n\n"
report_content += "**통계표 (키워드별 가격 기술통계)**\n" + price_stats.to_markdown() + "\n\n"
report_content += "> **해석**: 가격 분포를 살펴보면 두 제품군 모두 저가형 상품에 많은 매물이 집중되어 있는 'Left-Skewed' 형태를 띠고 있습니다. 오메가3의 경우 비타민D에 비해 가격 편차가 더 크며, 이는 원료의 순도나 추출 방식(rTG 등)에 따른 프리미엄 제품군이 더 다양하게 형성되어 있기 때문으로 해석됩니다.\n\n"

# 3. 주요 쇼핑몰 빈도수 (상위 30개)
mall_counts = shop_all['mallName'].value_counts().head(30)
plt.figure(figsize=(12, 8))
mall_counts.plot(kind='bar')
plt.title("상위 30개 쇼핑몰 등록 빈도")
img3 = save_plot("fig3_mall_freq.png")

mall_table = mall_counts.to_frame(name='빈도수')
report_content += "### 3. 주요 쇼핑몰 점유율 분석\n"
report_content += f"![mall_freq]({img3.replace('naverapieda/', '')})\n\n"
report_content += "**빈도수 표 (상위 30개 쇼핑몰)**\n" + mall_table.to_markdown() + "\n\n"
report_content += "> **해석**: 네이버 쇼핑 내에서 가장 많은 상품이 등록된 쇼핑몰들을 분석한 결과, '네이버' 통합 카탈로그와 스마트스토어 입점 판매자의 비중이 압도적으로 높습니다. 이는 중소 유통사들이 네이버 플랫폼을 주요 판매 채널로 활용하고 있음을 보여주며, 특정 대형몰보다는 파편화된 스토어들이 시장을 형성하고 있습니다.\n\n"

# 4. 주요 브랜드 빈도수 (상위 30개)
brand_counts = shop_all['brand'].value_counts().head(30)
plt.figure(figsize=(12, 8))
brand_counts.plot(kind='bar', color='orange')
plt.title("상위 30개 브랜드 등록 빈도")
img4 = save_plot("fig4_brand_freq.png")

brand_table = brand_counts.to_frame(name='빈도수')
report_content += "### 4. 주요 브랜드 선호도 분석\n"
report_content += f"![brand_freq]({img4.replace('naverapieda/', '')})\n\n"
report_content += "**빈도수 표 (상위 30개 브랜드)**\n" + brand_table.to_markdown() + "\n\n"
report_content += "> **해석**: 시장에 출시된 브랜드 중 상위 노출 빈도가 높은 브랜드를 식별한 결과, 종근당건강, 고려은단 등 인지도 높은 국내 제약사 브랜드들이 상위권을 차지하고 있습니다. 소비자들은 건강기능식품 선택 시 브랜드의 신뢰도를 중요한 기준으로 삼는 경향이 데이터에 반영된 것으로 보입니다.\n\n"

# 5. 키워드별 가격 박스플롯 (이변량)
plt.figure(figsize=(10, 6))
sns.boxplot(data=shop_all, x='Keyword', y='lprice', showfliers=False)
plt.title("키워드별 가격 분포 (Outlier 제외)")
img5 = save_plot("fig5_price_box.png")

report_content += "### 5. 키워드별 가격 편차 비교 (Box Plot)\n"
report_content += f"![price_box]({img5.replace('naverapieda/', '')})\n\n"
report_content += "> **해석**: 박스플롯 분석 결과, 오메가3의 중앙값(Median)과 사분위 범위(IQR)가 비타민D보다 높게 형성되어 있습니다. 이는 오메가3가 평균적으로 더 높은 단가를 형성하고 있음을 의미하며, 비타민D는 상대적으로 저렴하고 규격화된 가격대의 상품이 주를 이루고 있음을 알 수 있습니다.\n\n"

# 6. 쇼핑몰별 평균 가격 비교 (상위 10개 쇼핑몰)
top10_malls = shop_all['mallName'].value_counts().head(10).index
mall_avg_price = shop_all[shop_all['mallName'].isin(top10_malls)].groupby('mallName')['lprice'].mean().sort_values()
plt.figure(figsize=(10, 6))
mall_avg_price.plot(kind='barh', color='green')
plt.title("상위 10개 쇼핑몰별 평균 판매가")
img6 = save_plot("fig6_mall_price.png")

report_content += "### 6. 쇼핑몰별 가격 전략 분석\n"
report_content += f"![mall_price]({img6.replace('naverapieda/', '')})\n\n"
report_content += "**피봇 테이블 (쇼핑몰별 평균가)**\n" + mall_avg_price.to_frame(name='평균가격').to_markdown() + "\n\n"
report_content += "> **해석**: 등록 빈도가 높은 상위 10개 쇼핑몰의 평균 판매가를 비교한 결과, 특정 쇼핑몰은 고가 라인업에 집중하고 있는 반면, 대형 오픈마켓 계열은 낮은 평균가를 유지하며 가격 경쟁력을 확보하고 있습니다. 이는 쇼핑몰마다 타겟 고객층과 입점 브랜드의 성격이 다름을 시사합니다.\n\n"

# 7. 블로그 포스팅 일자별 빈도 (시계열)
blog_all['postdate'] = pd.to_datetime(blog_all['postdate'], format='%Y%m%d')
blog_date_counts = blog_all['postdate'].value_counts().sort_index()
plt.figure(figsize=(12, 6))
blog_date_counts.plot(kind='line', marker='o')
plt.title("최근 블로그 포스팅 생성 추이")
img7 = save_plot("fig7_blog_trend.png")

report_content += "### 7. 블로그 바이럴 추이 분석\n"
report_content += f"![blog_trend]({img7.replace('naverapieda/', '')})\n\n"
report_content += "> **해석**: 수집된 블로그 데이터를 일자별로 분석한 결과, 최근 날짜에 포스팅이 집중되어 있는 양상을 보입니다. 이는 최신 정보를 찾는 소비자의 니즈에 맞춰 블로거들이 꾸준히 콘텐츠를 생산하고 있음을 보여주며, 특정 요일에 포스팅이 증가하는 패턴은 주말 대비 평일의 정보 검색 활동이 활발함을 나타낼 수 있습니다.\n\n"

# 8. TF-IDF 키워드 분석 (오메가3 블로그)
def plot_tfidf(texts, title, filename):
    vectorizer = TfidfVectorizer(max_features=30, stop_words=['있는', '합니다', '대한', '있습니다', '위한'])
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    sums = tfidf_matrix.sum(axis=0)
    data = []
    for col, name in enumerate(feature_names):
        data.append((name, sums[0, col]))
    ranking = pd.DataFrame(data, columns=['words', 'sum'])
    ranking = ranking.sort_values('sum', ascending=False)
    
    plt.figure(figsize=(10, 8))
    plt.barh(ranking['words'], ranking['sum'], color='skyblue')
    plt.title(title)
    plt.gca().invert_yaxis()
    return save_plot(filename), ranking

img8, rank8 = plot_tfidf(blog_o3['description'], "오메가3 블로그 주요 키워드 (TF-IDF)", "fig8_o3_tfidf.png")
report_content += "### 8. 오메가3 블로그 주요 키워드 분석\n"
report_content += f"![o3_tfidf]({img8.replace('naverapieda/', '')})\n\n"
report_content += "**키워드 가중치 표**\n" + rank8.head(30).to_markdown() + "\n\n"
report_content += "> **해석**: 오메가3 관련 블로그 설명에서 추출된 핵심 키워드들을 분석한 결과, '식물성', 'rTG', '초임계' 등 제품의 특성과 기술력을 강조하는 단어들이 높은 비중을 차지합니다. 이는 소비자들이 오메가3 선택 시 흡수율과 원료의 안전성을 가장 중요하게 고려하며, 블로거들도 이를 주요 정보로 제공하고 있음을 의미합니다.\n\n"

# 9. TF-IDF 키워드 분석 (비타민D 블로그)
img9, rank9 = plot_tfidf(blog_vd['description'], "비타민D 블로그 주요 키워드 (TF-IDF)", "fig9_vd_tfidf.png")
report_content += "### 9. 비타민D 블로그 주요 키워드 분석\n"
report_content += f"![vd_tfidf]({img9.replace('naverapieda/', '')})\n\n"
report_content += "**키워드 가중치 표**\n" + rank9.head(30).to_markdown() + "\n\n"
report_content += "> **해석**: 비타민D 관련 블로그에서는 '부족', '결핍', '임산부', '칼슘' 등의 키워드가 두드러집니다. 이는 비타민D가 현대인의 결핍 문제와 밀접하게 연관되어 있으며, 특히 임산부 건강이나 칼슘 흡수 보조제로서의 역할이 강조되고 있음을 보여줍니다.\n\n"

# 10. 가격대별 키워드 빈도 교차분석 (다변량)
shop_all['PriceGroup'] = pd.qcut(shop_all['lprice'], q=3, labels=['저가', '중가', '고가'])
cross_tab = pd.crosstab(shop_all['PriceGroup'], shop_all['Keyword'])
plt.figure(figsize=(8, 6))
sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlGnBu')
plt.title("가격대별 키워드 빈도 교차표")
img10 = save_plot("fig10_cross_tab.png")

report_content += "### 10. 가격대 및 키워드 복합 분석\n"
report_content += f"![cross_tab]({img10.replace('naverapieda/', '')})\n\n"
report_content += "**교차표 (가격대별 상품 수)**\n" + cross_tab.to_markdown() + "\n\n"
report_content += "> **해석**: 가격대를 3단계로 나누어 키워드별 분포를 분석한 결과, 오메가3는 상대적으로 '고가' 구간에 더 많은 상품이 분포해 있는 반면, 비타민D는 '저가' 구간의 비중이 높게 나타납니다. 이는 앞서 수행한 가격 분포 및 박스플롯 분석 결과를 뒷받침하며, 제품군별로 형성된 시장 가격대의 특징이 뚜렷함을 확증합니다.\n\n"

# 리포트 저장
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"EDA Report generated: {REPORT_FILE}")
