import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Set Korean Font (AppleGothic for macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")
DETAIL_CSV = os.path.join(DATA_DIR, "iherb_sleep_products_detailed.csv")

def run_performance_and_pdp_analysis():
    print("Loading data from DB...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM iherb_sleep_products", conn)
    conn.close()

    if 'main_active' not in df.columns:
        df['product_name_lower'] = df['product_name'].str.lower()
        df['main_active'] = '기타단일체'
        df.loc[df['product_name_lower'].str.contains('melatonin|멜라토닌'), 'main_active'] = 'melatonin'
        df.loc[df['product_name_lower'].str.contains('magnesium|마그네슘'), 'main_active'] = 'magnesium'
        df.loc[df['product_name_lower'].str.contains('valerian|passion|chamomile|발레리안|카모마일'), 'main_active'] = 'valerian'
        df.loc[df['product_name_lower'].str.contains('formula|complex|sleep|rest|blend'), 'main_active'] = '기타/복합'

    def get_segment(main_active):
        if main_active == 'melatonin': return '멜라토닌'
        if main_active == 'magnesium': return '마그네슘'
        if main_active in ['valerian', 'chamomile', 'passionflower']: return '천연 허브'
        if main_active == '기타/복합': return '복합 포뮬러'
        return '기타 단일체'
    
    df['segment'] = df['main_active'].apply(get_segment)

    # ---------------------------------------------------------
    # 1. Performance Layer: Rating & Review Count by Segment
    # ---------------------------------------------------------
    perf_df = df[df['segment'].isin(['멜라토닌', '마그네슘', '천연 허브', '복합 포뮬러'])]
    
    # Calculate means
    segment_perf = perf_df.groupby('segment').agg(
        avg_rating=('rating', 'mean'),
        avg_reviews=('review_count', 'mean'),
        avg_price=('price', 'mean')
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart for Review Count (Primary Y)
    sns.barplot(data=segment_perf, x='segment', y='avg_reviews', color='skyblue', alpha=0.8, ax=ax1, errorbar=None)
    ax1.set_ylabel('평균 리뷰 수', color='tab:blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xlabel('성분 세그먼트', fontsize=12)

    # Add text on bars
    for i, v in enumerate(segment_perf['avg_reviews']):
        ax1.text(i, v + 200, f"{int(v):,}건", ha='center', color='black', fontweight='bold')

    # Line chart for Rating (Secondary Y)
    ax2 = ax1.twinx()
    sns.lineplot(data=segment_perf, x='segment', y='avg_rating', color='red', marker='o', markersize=10, linewidth=3, ax=ax2)
    ax2.set_ylabel('평균 평점 (5점 만점)', color='red', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(4.4, 4.8) # Zoom in to see differences 

    # Add text on line points
    for i, v in enumerate(segment_perf['avg_rating']):
        ax2.text(i, v + 0.02, f"{v:.2f}점", ha='center', color='red', fontweight='bold')

    plt.title('성분 레이어별 퍼포먼스: 평균 리뷰 수 및 평점', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_performance_layer.png'), dpi=300)
    plt.close()

    # ---------------------------------------------------------
    # 2. Top 15 PDP Deep Dive: Magnesium Forms & Badges
    # ---------------------------------------------------------
    df_pdp = df[df['ingredient_snippet'].notnull() & (df['ingredient_snippet'] != '')].copy()
    print(f"Loaded {len(df_pdp)} products with detailed PDP data.")
    
    if len(df_pdp) > 0:
        # ---------------------------------------------------------
        # Which Magnesium forms dominate the Top 15?
        df_pdp['subcategory_lower'] = df_pdp['subcategory'].fillna('').str.lower() + ' ' + df_pdp['product_name'].fillna('').str.lower()
        
        form_counts = {
            'Glycinate (글리시네이트)': df_pdp['subcategory_lower'].str.contains('glycinate|글리시네이트|리시네이트').sum(),
            'Taurate (타우레이트)': df_pdp['subcategory_lower'].str.contains('taurate|타우레이트').sum(),
            'Threonate (트레오네이트)': df_pdp['subcategory_lower'].str.contains('threonate|트레오네이트').sum(),
            'Citrate (시트레이트)': df_pdp['subcategory_lower'].str.contains('citrate|시트레이트|구연산').sum(),
            'Oxide (산화 마그네슘)': df_pdp['subcategory_lower'].str.contains('oxide|산화').sum()
        }
        
        forms_series = pd.Series(form_counts).sort_values(ascending=False)
        forms_series = forms_series[forms_series > 0] # drop zeros
        
        plt.figure(figsize=(10, 5))
        sns.barplot(orient='h', x=forms_series.values, y=forms_series.index, color='purple')
        for i, v in enumerate(forms_series.values):
            plt.text(v + 0.1, i, f"{int(v)}개", va='center')
        plt.title('Top 15 메가 베스트셀러 내 마그네슘 형태(Form) 분석 (이름/카테고리)', fontsize=14, pad=15)
        plt.xlabel('포함된 제품 수', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(DATA_DIR, 'chart_top15_magnesium_forms.png'), dpi=300)
        plt.close()

        # ---------------------------------------------------------
        # Badges Analysis (parsing from name and ingredient snippet since badges col might be empty)
        df_pdp['search_text'] = df_pdp['badges'].fillna('').str.lower() + ' ' + df_pdp['product_name'].str.lower() + ' ' + df_pdp['ingredient_snippet'].fillna('').str.lower()
        badge_counts = {
            'Vegan / Veggie (비건/식물성)': df_pdp['search_text'].str.contains('vegan|비건|veggie|식물성캡슐|베지 캡슐').sum(),
            'Gluten Free (글루텐 프리)': df_pdp['search_text'].str.contains('gluten|글루텐').sum(),
            'Non-GMO (유전자 변형 없음)': df_pdp['search_text'].str.contains('gmo|유전자 변형').sum(),
            'GMP Quality (품질 보증)': df_pdp['search_text'].str.contains('gmp|우수 제조|품질 보증|quality').sum(),
            'Sleep/Relax (숙면/이완)': df_pdp['search_text'].str.contains('sleep|rest|유도|숙면|이완').sum()
        }
        badges_series = pd.Series(badge_counts).sort_values(ascending=False)
        badges_series = badges_series[badges_series > 0]

        plt.figure(figsize=(10, 5))
        sns.barplot(orient='h', x=badges_series.values, y=badges_series.index, color='teal')
        for i, v in enumerate(badges_series.values):
            plt.text(v + 0.1, i, f"{int(v)}개", va='center')
        plt.title('Top 15 메가 베스트셀러 마케팅 클레임 및 뱃지 분석', fontsize=14, pad=15)
        plt.xlabel('포함된 제품 수', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(DATA_DIR, 'chart_top15_badges.png'), dpi=300)
        plt.close()

    print("✅ Performance and Top 15 visual charts generated successfully.")

if __name__ == '__main__':
    run_performance_and_pdp_analysis()
