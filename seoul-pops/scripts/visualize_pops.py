import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Korean font for Mac
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False

def visualize():
    base_dir = "/Users/kimyo/Documents/PARA/1_Project/Antigravity/fcicb7/seoul-pops"
    parquet_path = os.path.join(base_dir, "data/processed/seoul_pops_tidy.parquet")
    img_dir = os.path.join(base_dir, "docs/images")
    os.makedirs(img_dir, exist_ok=True)
    
    print("Loading data...")
    df = pd.read_parquet(parquet_path)
    
    # 1. Top 10 Sigungu
    print("Creating Sigungu chart...")
    plt.figure(figsize=(12, 6))
    gu_data = df.groupby("sigungu_name")["pop_count"].sum().sort_values(ascending=False).head(10)
    sns.barplot(x=gu_data.index, y=gu_data.values, hue=gu_data.index, palette="viridis", legend=False)
    plt.title("서울시 주요 구별 생활인구 (Top 10)", fontsize=18)
    plt.xlabel("구명", fontsize=12)
    plt.ylabel("생활인구 합계", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "top_10_gu.png"))
    plt.close()

    # 2. Top 15 Dong
    print("Creating Dong chart...")
    plt.figure(figsize=(14, 7))
    dong_data = df.groupby("dong_name")["pop_count"].sum().sort_values(ascending=False).head(15)
    sns.barplot(x=dong_data.index, y=dong_data.values, hue=dong_data.index, palette="rocket", legend=False)
    plt.title("서울시 주요 행정동별 생활인구 (Top 15)", fontsize=18)
    plt.xlabel("행정동명", fontsize=12)
    plt.ylabel("생활인구 합계", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "top_15_dong.png"))
    plt.close()

    # 3. Hourly Trend
    print("Creating Hourly trend chart...")
    plt.figure(figsize=(12, 6))
    hour_trend = df.groupby("hour")["pop_count"].sum()
    sns.lineplot(x=hour_trend.index, y=hour_trend.values, marker='o', color='royalblue', linewidth=2.5)
    plt.title("시간대별 서울시 전체 생활인구 변화", fontsize=18)
    plt.xlabel("시간 (Hour)", fontsize=12)
    plt.ylabel("생활인구 합계", fontsize=12)
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "hourly_trend.png"))
    plt.close()

    # 4. Age & Gender Distribution
    print("Creating Age/Gender chart...")
    plt.figure(figsize=(14, 7))
    age_gender = df.groupby(["age_group", "gender"])["pop_count"].sum().reset_index()
    sns.barplot(data=age_gender, x="age_group", y="pop_count", hue="gender", palette="coolwarm")
    plt.title("연령대 및 성별 생활인구 분포", fontsize=18)
    plt.xlabel("연령대", fontsize=12)
    plt.ylabel("생활인구 합계", fontsize=12)
    plt.legend(title="성별")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, "age_gender_dist.png"))
    plt.close()

    print(f"All visualizations saved to {img_dir}")

if __name__ == "__main__":
    visualize()
