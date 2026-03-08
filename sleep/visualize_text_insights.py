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

def analyze_text_layer():
    print("Loading detailed data from DB for text analysis...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM iherb_sleep_products", conn)
    conn.close()
    
    # Check if 'badges' and 'ingredient_snippet' columns exist in DB 
    if 'badges' not in df.columns: df['badges'] = ''
    if 'ingredient_snippet' not in df.columns: df['ingredient_snippet'] = ''
    if 'main_active' not in df.columns:
        df['product_name_lower'] = df['product_name'].str.lower()
        df['main_active'] = '기타단일체'
        df.loc[df['product_name_lower'].str.contains('melatonin|멜라토닌'), 'main_active'] = 'melatonin'
        df.loc[df['product_name_lower'].str.contains('magnesium|마그네슘'), 'main_active'] = 'magnesium'
        df.loc[df['product_name_lower'].str.contains('valerian|passion|chamomile|발레리안|카모마일'), 'main_active'] = 'valerian'
        # 아래 줄은 단일제임에도 이름에 sleep이 들어간 경우 '복합제'로 오분류하므로 주석 처리하거나 제거합니다.
        # df.loc[df['product_name_lower'].str.contains('formula|complex|sleep|rest|blend'), 'main_active'] = '기타/복합'

    # Combine text fields into one text corpus per product (handle NaNs)
    df['text_corpus'] = (
        df['product_name'].fillna('') + ' ' + 
        df['badges'].fillna('') + ' ' + 
        df['ingredient_snippet'].fillna('')
    ).str.lower()
    
    # Define Need Keyword Dictionary (Bilingual for KR site)
    needs_dict = {
        '입면/신속 (Fast Sleep)': ['fall asleep', 'fast', 'quick', 'rapid', 'immediate', 'time release', 'onset', '빠른', '빨리', '금방', '속방형', '수면 유도', '잠들'],
        '수면유지/이완 (Deep/Relax)': ['stay asleep', 'deep', 'calm', 'relax', 'sooth', 'stress', 'muscle', 'restful', '숙면', '깊은', '유지', '수면 지원', '휴식', '진정', '이완', '스트레스', '편안'],
        '안전/자연주의 (Safe/Natural)': ['non-habit', 'drug-free', 'natural', 'safe', 'vegan', 'gmo', 'organic', 'vegetarian', '비건', '채식', '글루텐', '유전자 변형', '무첨가', '천연', '내성', '식물성']
    }
    
    # Count occurrences of needs
    for need, keywords in needs_dict.items():
        # returns True if any keyword is in the corpus
        df[need] = df['text_corpus'].apply(lambda t: any(kw in t for kw in keywords))
        
    # Group by ingredient segment (Melatonin, Magnesium, Herbs (valerian/chamomile/passionflower), Complex)
    # create a super segment
    def get_segment(main_active):
        if main_active == 'melatonin': return '멜라토닌'
        if main_active == 'magnesium': return '마그네슘'
        if main_active in ['valerian', 'chamomile', 'passionflower']: return '천연 허브'
        if main_active == '기타/복합': return '복합 포뮬러'
        return '기타 단일체'
    
    df['segment'] = df['main_active'].apply(get_segment)
    
    # Needs matrix (% of products in that segment mentioning the need)
    # We only care about main 4 segments
    target_segments = ['멜라토닌', '마그네슘', '천연 허브', '복합 포뮬러']
    matrix = df[df['segment'].isin(target_segments)].groupby('segment')[list(needs_dict.keys())].mean() * 100
    
    # Reindex instead of loc to handle missing categories with 0 instead of crashing
    matrix = matrix.reindex(target_segments).fillna(0)
    
    # Visualization: Heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5)
    plt.title('성분별 제품 텍스트(마케팅/뱃지) 소구 포인트 (키워드 등장 비율, %)', fontsize=14, pad=15)
    plt.ylabel('성분 세그먼트', fontsize=12)
    plt.xlabel('수면 니즈 및 소구점', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'chart_text_needs_heatmap.png'), dpi=300)
    plt.close()

    print("✅ Text layer analysis visualization generated successfully!")
    print(matrix)

if __name__ == '__main__':
    analyze_text_layer()
