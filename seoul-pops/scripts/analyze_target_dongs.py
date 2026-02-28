import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Korean font for Mac
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False

def analyze_targets():
    base_dir = "/Users/kimyo/Documents/PARA/1_Project/Antigravity/fcicb7/seoul-pops"
    parquet_path = os.path.join(base_dir, "data/processed/seoul_pops_tidy.parquet")
    img_dir = os.path.join(base_dir, "docs/images/targets")
    os.makedirs(img_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_parquet(parquet_path)
    
    available_dongs = df["dong_name"].unique()
    targets = ["연남동", "성수1가1동", "성수1가2동", "성수2가1동", "성수2가3동", "역삼1동", "역삼2동"]
    
    results_md = []
    
    for dong in targets:
        if dong not in available_dongs:
            print(f"Skipping {dong} (not in data)")
            continue
            
        print(f"Processing {dong}...")
        dong_df = df[df["dong_name"] == dong]
        
        # 1. Hourly Line Graph
        plt.figure(figsize=(10, 5))
        hour_trend = dong_df.groupby("hour")["pop_count"].sum()
        sns.lineplot(x=hour_trend.index, y=hour_trend.values, marker='o', color='teal', linewidth=2)
        plt.title(f"{dong} 시간대별 생활인구 흐름", fontsize=15)
        plt.xlabel("시간 (Hour)")
        plt.ylabel("생활인구 합계")
        plt.xticks(range(0, 24))
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        line_path = os.path.join(img_dir, f"{dong}_hourly.png")
        plt.savefig(line_path)
        plt.close()

        # 2. Age-Hour Heatmap
        plt.figure(figsize=(12, 8))
        pivot_df = dong_df.pivot_table(index="age_group", columns="hour", values="pop_count", aggfunc="sum")
        sns.heatmap(pivot_df, cmap="YlGnBu", annot=False, fmt=".0f")
        plt.title(f"{dong} 연령대별-시간대별 생활인구 히트맵", fontsize=15)
        plt.xlabel("시간 (Hour)")
        plt.ylabel("연령대")
        plt.tight_layout()
        heatmap_path = os.path.join(img_dir, f"{dong}_heatmap.png")
        plt.savefig(heatmap_path)
        plt.close()

        # 3. Statistics
        stats = dong_df.groupby("hour")["pop_count"].sum().describe().to_frame().T
        stats_md = stats.to_markdown()

        # 4. Crosstab (Age vs Hour - 2 hour intervals)
        ctraw = dong_df.pivot_table(index="age_group", columns="hour", values="pop_count", aggfunc="sum")
        ctraw_md = ctraw.iloc[:, ::2].to_markdown()

        # Construct MD snippet
        results_md.append(f"""
### 📍 {dong} 상세 분석

#### [시간대별 흐름 및 인구 구조]
![{dong} Hourly Trend](images/targets/{dong}_hourly.png)
![{dong} Heatmap](images/targets/{dong}_heatmap.png)

#### 기술통계 (시간대별 총 생활인구)
{stats_md}

#### 시간대별 연령별 교차표 (2시간 간격 요약)
{ctraw_md}

---
""")

    # Write the snippets to a temp file
    with open(os.path.join(base_dir, "docs/target_analysis_snippet.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(results_md))

    print("Target analysis completed.")

if __name__ == "__main__":
    analyze_targets()
