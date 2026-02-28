import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set Korean Font (AppleGothic for macOS)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SUMMARY_CSV = os.path.join(DATA_DIR, "iherb_sleep_summary_by_active.csv")
DETAIL_CSV = os.path.join(DATA_DIR, "iherb_sleep_products_detailed.csv")

def create_visualizations():
    if not os.path.exists(SUMMARY_CSV):
        print("Summary CSV not found.")
        return

    df_summary = pd.read_csv(SUMMARY_CSV)
    
    # 1. Bubble Chart: Price vs Rating (Size = Reviews)
    plt.figure(figsize=(12, 8))
    
    # Bubble size: Scale total_reviews for better visualization (e.g. min size, max size constraint)
    sizes = df_summary['total_reviews'] / df_summary['total_reviews'].max() * 5000 + 100
    
    scatter = sns.scatterplot(
        data=df_summary,
        x='avg_price',
        y='avg_rating',
        size='total_reviews',
        sizes=(100, 5000),
        hue='main_active',
        palette='tab10',
        alpha=0.7,
        edgecolor='w'
    )
    
    # Annotate points
    for i in range(len(df_summary)):
        if df_summary.loc[i, 'n_products'] >= 1: # annotate all
            plt.text(
                df_summary.loc[i, 'avg_price'], 
                df_summary.loc[i, 'avg_rating'], 
                df_summary.loc[i, 'main_active'], 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=10,
                weight='bold'
            )
            
    plt.title('성분별 평균 가격 vs 평균 평점 (버블: 리뷰 수)', fontsize=16, pad=20)
    plt.xlabel('평균 가격 (KRW)', fontsize=12)
    plt.ylabel('평균 평점 (5점 만점)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Remove legends that clutters
    plt.legend([],[], frameon=False)
    
    chart1_path = os.path.join(DATA_DIR, 'chart_price_vs_rating.png')
    plt.tight_layout()
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved: {chart1_path}")

    # 2. Bar Chart: SKU count vs Total Reviews (Fandom strength)
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Sort by total_reviews for better flow
    df_sorted = df_summary.sort_values('total_reviews', ascending=False)
    
    # Bar plot for SKU Count
    sns.barplot(
        data=df_sorted, 
        x='main_active', 
        y='n_products', 
        ax=ax1, 
        color='skyblue', 
        alpha=0.8,
        label='SKU 수 (제품 수)'
    )
    
    # Line plot for Total Reviews on secondary Y axis
    ax2 = ax1.twinx()
    sns.lineplot(
        data=df_sorted, 
        x='main_active', 
        y='total_reviews', 
        ax=ax2, 
        color='coral', 
        marker='o', 
        linewidth=2,
        markersize=10,
        label='총 리뷰 수 (팬덤/수요 강도)'
    )
    
    ax1.set_title('성분별 제품 수(SKU) vs 총 리뷰 수 (시장 집중도)', fontsize=16, pad=20)
    ax1.set_xlabel('주요 성분', fontsize=12)
    ax1.set_ylabel('제품 수 (SKU)', fontsize=12, color='skyblue')
    ax2.set_ylabel('총 리뷰 수', fontsize=12, color='coral')
    
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
    
    chart2_path = os.path.join(DATA_DIR, 'chart_sku_vs_reviews.png')
    plt.tight_layout()
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved: {chart2_path}")

if __name__ == '__main__':
    create_visualizations()
