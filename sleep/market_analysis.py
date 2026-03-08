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

# Differentiated Ingredient Groups
INGREDIENTS_GROUPS = {
    "Direct_Sleep_Aids": {
        "Melatonin": ["melatonin", "멜라토닌"],
        "L-Theanine": ["theanine", "테아닌"],
        "GABA": ["gaba", "가바"],
        "5-HTP": ["5-htp", "5 htp", "5htp"],
        "L-Tryptophan": ["tryptophan", "트립토판"],
        "Glycine": ["glycine", "글리신"],
        "Tart Cherry": ["tart cherry", "타트체리", "타트 체리"],
        "Lactium": ["lactium", "락티움"],
        "Apigenin": ["apigenin", "아피게닌"]
    },
    "Sedative_Herbs": {
        "Valerian Root": ["valerian", "발레리안", "쥐오줌풀"],
        "Passionflower": ["passion flower", "passionflower", "시계꽃", "패션플라워"],
        "Lemon Balm": ["lemon balm", "레몬밤", "레몬 밤"],
        "Chamomile": ["chamomile", "카모마일", "캐모마일"],
        "Ashwagandha": ["ashwagandha", "아슈와간다"],
        "Hops": ["hops", "홉"],
        "Skullcap": ["skullcap", "스컬캡"],
        "Magnolia": ["magnolia", "후박"],
        "Ziziphus/Jujube": ["ziziphus", "jujube", "산조인", "대추"],
        "Lavender": ["lavender", "라벤더"]
    },
    "Supportive_Nutrients": {
        "Magnesium": ["magnesium", "마그네슘"],
        "Vitamin B6": ["vitamin b6", "vitamin b-6", "비타민 b6", "비타민 b-6", "피리독신"],
        "Calcium": ["calcium", "칼슘"],
        "Zinc": ["zinc", "아연"],
        "B-Vitamins": ["vitamin b", "비타민 b"]
    }
}

def analyze_full_market():
    print("🚀 전체 수집 데이터 기반 성분 시장 분석 중...")
    
    conn = sqlite3.connect(DB_PATH)
    # Get all products, emphasizing the ones with snippets
    df = pd.read_sql_query("SELECT product_name, ingredient_snippet, subcategory, review_count FROM iherb_sleep_products", conn)
    conn.close()

    if df.empty:
        print("❌ 데이터가 없습니다.")
        return

    # Create search corpus (Title + Snippet)
    df['corpus'] = (df['product_name'].fillna('') + " " + df['ingredient_snippet'].fillna('')).str.lower()
    
    # Analyze Frequency
    all_ingredients = []
    for gname, items in INGREDIENTS_GROUPS.items():
        for name, keywords in items.items():
            has_it = df['corpus'].apply(lambda tx: any(kw in tx for kw in keywords))
            count = has_it.sum()
            avg_reviews = df[has_it]['review_count'].mean() if count > 0 else 0
            all_ingredients.append({
                "Group": gname,
                "Ingredient": name,
                "Count": count,
                "Avg_Reviews": avg_reviews,
                "Market_Share": (count / len(df)) * 100
            })
    
    results_df = pd.DataFrame(all_ingredients).sort_values("Count", ascending=False)
    
    print("\n📊 성분별 시장 점유율 (432개 제품 전체):")
    print(results_df[results_df['Count'] > 0])
    
    # 1. Ingredient Count Chart
    plt.figure(figsize=(12, 10))
    sns.barplot(data=results_df[results_df['Count'] > 0], x='Count', y='Ingredient', hue='Group', dodge=False)
    plt.title('수면 카테고리 전체 제품 성분 분포 (중복 포함)', fontsize=16, pad=20)
    plt.xlabel('제품 수', fontsize=12)
    plt.ylabel('성분명', fontsize=12)
    plt.legend(title='성분 그룹', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_full_market_ingredients.png'), dpi=300)
    plt.close()

    # 2. Formula Segmentation Analysis
    # Identifying Magnesium vs Non-Magnesium Sleep Aids
    df['is_magnesium'] = df['corpus'].str.contains('magnesium|마그네슘', na=False)
    df['is_sleep_specific'] = df['corpus'].apply(lambda tx: any(kw in tx for g in ["Direct_Sleep_Aids", "Sedative_Herbs"] for items in [INGREDIENTS_GROUPS[g]] for item in items.values() for kw in item))
    
    segments = {
        "Pure Magnesium": df[df['is_magnesium'] & ~df['is_sleep_specific']],
        "Magnesium + Sleep Aids": df[df['is_magnesium'] & df['is_sleep_specific']],
        "Sleep Aids (No Magnesium)": df[~df['is_magnesium'] & df['is_sleep_specific']],
        "Others/Misc": df[~df['is_magnesium'] & ~df['is_sleep_specific']]
    }
    
    seg_stats = []
    for sname, sdf in segments.items():
        seg_stats.append({
            "Segment": sname,
            "Count": len(sdf),
            "Avg_Reviews": sdf['review_count'].mean()
        })
    
    seg_df = pd.DataFrame(seg_stats)
    print("\n📀 세그먼트별 분포:")
    print(seg_df)
    
    # Visualization: Pie Chart
    plt.figure(figsize=(10, 8))
    plt.pie(seg_df['Count'], labels=seg_df['Segment'], autopct='%1.1f%%', startangle=140, colors=['#3498db', '#9b59b6', '#27ae60', '#bdc3c7'])
    plt.title('수면 보조제 시장 세그먼트 구성비', fontsize=15)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_market_segments_pie.png'), dpi=300)
    plt.close()

    print(f"\n✅ 분석 결과 저장 완료!")

if __name__ == "__main__":
    analyze_full_market()
