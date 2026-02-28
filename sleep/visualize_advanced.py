import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Set Korean Font (AppleGothic for macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")
DETAIL_CSV = os.path.join(DATA_DIR, "iherb_sleep_products_detailed.csv")

def run_advanced_visualizations():
    # Load detailed data
    df = pd.read_csv(DETAIL_CSV)

    # Clean data
    df = df[df['price'] > 0]
    df = df.dropna(subset=['brand'])

    # 1. Top Brands Market Share (By Review Count)
    brand_summary = df.groupby('brand').agg(
        total_reviews=('review_count', 'sum'),
        sku_count=('product_id', 'count')
    ).reset_index().sort_values('total_reviews', ascending=False).head(15)

    plt.figure(figsize=(14, 7))
    sns.barplot(data=brand_summary, y='brand', x='total_reviews', palette='viridis')
    plt.title('수면 영양제 시장 Top 15 브랜드 (리뷰 수 기준 시장 점유율)', fontsize=16, pad=20)
    plt.xlabel('총 리뷰 수 (충성도 및 판매 규모)', fontsize=12)
    plt.ylabel('브랜드 (Brand)', fontsize=12)
    for index, value in enumerate(brand_summary['total_reviews']):
        plt.text(value + 10000, index, f'{value:,}', va='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_brand_market_share.png'), dpi=300)
    plt.close()

    # 2. Price Distribution (Sweet Spot Analysis)
    plt.figure(figsize=(12, 6))
    sns.histplot(df['price'], bins=40, kde=True, color='teal', alpha=0.6)
    median_price = df['price'].median()
    plt.axvline(median_price, color='red', linestyle='dashed', linewidth=2, label=f'중앙값: {median_price:,.0f}원')
    plt.title('전체 제품 가격대 분포 (Sweet Spot 분석)', fontsize=16, pad=20)
    plt.xlabel('가격 (KRW)', fontsize=12)
    plt.ylabel('제품 수 (Frequency)', fontsize=12)
    plt.xlim(0, 80000) # Exclude extreme outliers for better visibility
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_price_distribution.png'), dpi=300)
    plt.close()

    # 3. Price & Rating Boxplot by Main Active Ingredient
    top_ingredients = df['main_active'].value_counts().head(7).index
    df_top_ings = df[df['main_active'].isin(top_ingredients)]
    
    plt.figure(figsize=(14, 6))
    sns.boxplot(data=df_top_ings, x='main_active', y='price', palette='Set2')
    plt.title('주요 성분별 가격대 편차 (Boxplot)', fontsize=16, pad=20)
    plt.xlabel('주요 성분 (Main Active)', fontsize=12)
    plt.ylabel('가격 (KRW)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_ingredient_price_boxplot.png'), dpi=300)
    plt.close()

    print("✅ Advanced visualizations generated successfully!")
    print(f"- chart_brand_market_share.png")
    print(f"- chart_price_distribution.png")
    print(f"- chart_ingredient_price_boxplot.png")

if __name__ == '__main__':
    run_advanced_visualizations()
