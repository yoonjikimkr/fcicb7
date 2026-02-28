import pandas as pd
import os

def process_data():
    base_dir = "/Users/kimyo/Documents/PARA/1_Project/Antigravity/fcicb7/seoul-pops"
    raw_csv = os.path.join(base_dir, "data/raw/LOCAL_PEOPLE_DONG_202601.csv")
    mapping_xlsx = os.path.join(base_dir, "data/processed/mapping_info.xlsx")
    output_parquet = os.path.join(base_dir, "data/processed/seoul_pops_tidy.parquet")
    output_csv = os.path.join(base_dir, "data/processed/seoul_pops_tidy_202601.csv")

    print("Loading data...")
    # Define column names
    meta_cols = ["date", "hour", "dong_code", "total_pop"]
    age_groups = ["0009", "1014", "1519", "2024", "2529", "3034", "3539", "4044", "4549", "5054", "5559", "6064", "6569", "70up"]
    male_cols = [f"M{g}" for g in age_groups]
    female_cols = [f"F{g}" for g in age_groups]
    all_cols = meta_cols + male_cols + female_cols + ["extra"]

    # Read CSV (skip header row)
    df = pd.read_csv(raw_csv, names=all_cols, index_col=False, skiprows=1)
    df = df.drop(columns=["extra"])

    print("Loading mapping info...")
    mapping_df = pd.read_excel(mapping_xlsx)
    # The first row contains headers like H_SDNG_CD, H_DNG_CD
    mapping_df.columns = mapping_df.iloc[0]
    mapping_df = mapping_df[1:]
    mapping_df = mapping_df[["H_DNG_CD", "CT_NM", "H_DNG_NM"]].rename(columns={
        "H_DNG_CD": "dong_code",
        "CT_NM": "sigungu_name",
        "H_DNG_NM": "dong_name"
    })
    
    # Ensure dong_code is same type for joining
    df["dong_code"] = df["dong_code"].astype(str)
    mapping_df["dong_code"] = mapping_df["dong_code"].astype(str)

    print("Merging with dong names...")
    df = df.merge(mapping_df, on="dong_code", how="left")

    print("Making data tidy...")
    # Melt age/gender columns
    value_cols = male_cols + female_cols
    tidy_df = df.melt(
        id_vars=["date", "hour", "dong_code", "sigungu_name", "dong_name", "total_pop"],
        value_vars=value_cols,
        var_name="segment",
        value_name="pop_count"
    )

    # Split segment into gender and age_group
    tidy_df["gender"] = tidy_df["segment"].apply(lambda x: "Male" if x.startswith("M") else "Female")
    tidy_df["age_group"] = tidy_df["segment"].apply(lambda x: x[1:])
    tidy_df = tidy_df.drop(columns=["segment"])

    # Basic cleaning
    tidy_df["date"] = pd.to_datetime(tidy_df["date"].astype(str), format="%Y%m%d")
    
    # Final check on column names (Gu/Dong derived variables are already in sigungu_name and dong_name)
    # User might want separate gu/dong if they aren't explicit
    # sigungu_name = Gu, dong_name = Dong
    
    print(f"Saving tidy data to {output_parquet}...")
    tidy_df.to_parquet(output_parquet, index=False)
    
    # Keep CSV for size comparison this time, then we can delete
    # print(f"Saving temporary CSV for size comparison...")
    # tidy_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    
    print("Process completed successfully!")

if __name__ == "__main__":
    process_data()
