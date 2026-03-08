import os
import sqlite3
import pandas as pd
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")

def check_all_ingredients():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT product_name, ingredient_snippet FROM iherb_sleep_products ORDER BY review_count DESC LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()

    all_text = " ".join(df['ingredient_snippet'].fillna(""))
    # Find words that might be ingredients (mostly characters, maybe some numbers)
    # This is a bit loose but let's see.
    # We can also search for known keywords more thoroughly.
    
    keywords = {
        "Theanine": ["theanine", "테아닌"],
        "GABA": ["gaba", "가바"],
        "Valerian": ["valerian", "발레리안"],
        "Chamomile": ["chamomile", "카모마일", "캐모마일"],
        "Passionflower": ["passion", "패션플라워"],
        "Melatonin": ["melatonin", "멜라토닌"],
        "Ashwagandha": ["ashwagandha", "아슈와간다"],
        "5-HTP": ["5-htp", "5 htp"],
        "Tryptophan": ["tryptophan", "트립토판"],
        "Ziziphus": ["산조인", "산조", "ziziphus"],
        "Lemon Balm": ["lemon balm", "레몬밤"],
        "Apigenin": ["apigenin", "아피게닌"],
        "Lactium": ["lactium", "락티움"],
        "Saffron": ["saffron", "사프란", "샤프란"],
        "Holly": ["홀리", "holly"],
        "Relora": ["relora", "렐로라"],
        "Zinc": ["zinc", "아연"],
        "Glycine": ["glycine", "글리신"]
    }
    
    results = {}
    for key, kws in keywords.items():
        found = df[df['ingredient_snippet'].str.contains('|'.join(kws), case=False, na=False)]
        results[key] = len(found)
        
    print("Ingredient counts in TOP 100 Snippets:")
    for k, v in sorted(results.items(), key=lambda x: x[1], reverse=True):
        if v > 0:
            print(f" - {k}: {v}")
            
    # Check for anything else
    print("\nSample of non-magnesium snippets:")
    non_mag = df[~df['ingredient_snippet'].str.contains('magnesium|마그네슘', case=False, na=False)]
    for i, row in non_mag.head(10).iterrows():
        print(f"[{row['product_name']}] -> {row['ingredient_snippet'][:100]}...")

if __name__ == "__main__":
    check_all_ingredients()
