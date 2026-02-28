import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Korean Font (AppleGothic for macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DETAIL_CSV = os.path.join(DATA_DIR, "iherb_sleep_products_detailed.csv")

def analyze_all_ingredients():
    if not os.path.exists(DETAIL_CSV):
        print("Detailed CSV not found.")
        return

    df = pd.read_csv(DETAIL_CSV)
    
    # Drop rows without active ingredients
    df_valid = df.dropna(subset=['active_ingredients']).copy()
    
    # Convert comma-separated string to list
    df_valid['ingredient_list'] = df_valid['active_ingredients'].apply(lambda x: [i.strip() for i in x.split(',')])
    
    # Explode the list so each ingredient gets its own row for the same product
    df_exploded = df_valid.explode('ingredient_list')
    
    # Group by individual ingredient
    summary = df_exploded.groupby('ingredient_list').agg(
        n_products=('product_name', 'nunique'),
        avg_price=('price', 'mean'),
        avg_rating=('rating', 'mean'),
        total_reviews=('review_count', 'sum')
    ).reset_index().sort_values('n_products', ascending=False)
    
    # Print the true summary
    print("=== True Ingredient Occurrence (Including Complex Formulas) ===")
    print(summary.to_string(index=False))
    
    # Save the true summary
    summary.to_csv(os.path.join(DATA_DIR, 'iherb_true_ingredient_frequency.csv'), index=False)
    
    # Create Visualization
    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=summary,
        x='ingredient_list',
        y='n_products',
        color='mediumpurple',
        alpha=0.8
    )
    plt.title('전체 제품 내 개별 성분 포함 빈도 (복합제 포함)', fontsize=16, pad=20)
    plt.xlabel('개별 성분', fontsize=12)
    plt.ylabel('포함된 제품 수 (SKU)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Add data labels on top of bars
    for i, row in enumerate(summary.itertuples()):
        plt.text(i, row.n_products + 2, f"{row.n_products}개", ha='center', fontsize=10)
        
    chart_path = os.path.join(DATA_DIR, 'chart_true_ingredient_frequency.png')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"Saved: {chart_path}")

if __name__ == '__main__':
    analyze_all_ingredients()
