import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Korean Font (AppleGothic for macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")

# Expanded ACTIVES_MAP for deeper ingredient scanning
ACTIVES_MAP = {
    "Magnesium": ["magnesium", "마그네슘"],
    "Vitamin B6": ["vitamin b6", "vitamin b-6", "비타민 b6", "비타민 b-6", "피리독신"],
    "Calcium": ["calcium", "칼슘"],
    "Zinc": ["zinc", "아연"],
    "Glycine": ["glycine", "글리신"],
    "Valerian Root": ["valerian", "발레리안", "쥐오줌풀"],
    "Passionflower": ["passion flower", "passionflower", "시계꽃", "패션플라워"],
    "Hops": ["hops", "홉"],
    "L-Theanine": ["theanine", "테아닌"],
    "GABA": ["gaba", "가바"],
    "5-HTP": ["5-htp", "5 htp", "5htp"],
    "Chamomile": ["chamomile", "카모마일", "캐모마일"],
    "Lemon Balm": ["lemon balm", "레몬밤", "레몬 밤"],
    "Melatonin": ["melatonin", "멜라토닌"],
    "L-Tryptophan": ["tryptophan", "트립토판"],
    "Ashwagandha": ["ashwagandha", "아슈와간다"],
    "Tart Cherry": ["tart cherry", "타트 체리", "타트체리"],
    "Apigenin": ["apigenin", "아피게닌"],
    "Lavender": ["lavender", "라벤더"],
    "Potassium": ["potassium", "칼륨", "가리"],
}

def analyze_top_100_ingredients():
    print("🚀 상위 100개 제품의 실제 성분(Ingredient Snippet 포함) 분석을 시작합니다...")
    
    conn = sqlite3.connect(DB_PATH)
    # Get top 100 products by review count
    query = """
    SELECT product_name, ingredient_snippet, subcategory 
    FROM iherb_sleep_products 
    ORDER BY review_count DESC 
    LIMIT 100
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("❌ 분석할 데이터가 없습니다.")
        return

    # Combine name and snippet for searching (fill NaNs)
    df['search_text'] = (df['product_name'].fillna('') + " " + df['ingredient_snippet'].fillna('')).str.lower()
    
    # Tag logical existence of each ingredient
    ingredient_counts = {}
    for ingredient, keywords in ACTIVES_MAP.items():
        count = df['search_text'].apply(lambda tx: any(kw in tx for kw in keywords)).sum()
        ingredient_counts[ingredient] = count
    
    # Convert to DataFrame for visualization
    results_df = pd.DataFrame(list(ingredient_counts.items()), columns=['Ingredient', 'Count'])
    results_df = results_df.sort_values('Count', ascending=False)
    
    # Percentage calculation
    results_df['Percentage'] = (results_df['Count'] / len(df)) * 100
    
    print("\n📊 상위 100개 베스트셀러 성분 포함 분포:")
    print(results_df[results_df['Count'] > 0])
    
    # Visualization
    plt.figure(figsize=(12, 8))
    sns.barplot(data=results_df[results_df['Count'] > 0], x='Percentage', y='Ingredient', palette='viridis')
    
    for i, p in enumerate(results_df[results_df['Count'] > 0]['Percentage']):
        plt.text(p + 0.5, i, f'{p:.0f}%', va='center')

    plt.title('상위 100개 베스트셀러 내 성분 포함률 (%)', fontsize=16, pad=20)
    plt.xlabel('포함된 제품 비율 (%)', fontsize=12)
    plt.ylabel('성분명', fontsize=12)
    plt.xlim(0, 100)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_path = os.path.join(DATA_DIR, 'chart_best100_ingredient_distribution.png')
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"✅ 분석 완료! 차트가 저장되었습니다: {output_path}")

if __name__ == "__main__":
    analyze_top_100_ingredients()
