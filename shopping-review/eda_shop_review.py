import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
import os

# Set working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove special characters and numbers (optional, keeping some for context)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.strip()

def run_eda(file_path):
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Basic Info
    print("\n--- Basic Information ---")
    print(df.info())
    print("\n--- Null Values ---")
    print(df.isnull().sum())
    
    # Clean content
    print("\nCleaning text content...")
    df['clean_content'] = df['content'].apply(clean_text)
    df['content_length'] = df['clean_content'].str.len()
    
    # Summary Statistics for review length
    print("\n--- Review Length Statistics ---")
    print(df['content_length'].describe())
    
    # Visualization: Review Length Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['content_length'], bins=50, kde=True, color='skyblue')
    plt.title('Distribution of Review Lengths')
    plt.xlabel('Length (characters)')
    plt.ylabel('Frequency')
    plt.savefig('plots/review_length_dist.png')
    plt.close()
    
    # Top Keywords (Simple approach for Korean/English mix)
    # Note: For better Korean analysis, a library like Konlpy would be better, 
    # but we'll start with simple space-based tokenization.
    all_text = " ".join(df['clean_content'])
    words = all_text.split()
    # Filter out very short words
    words = [w for w in words if len(w) > 1]
    word_counts = Counter(words).most_common(20)
    
    print("\n--- Top 20 Keywords ---")
    for word, count in word_counts:
        print(f"{word}: {count}")
    
    # Visualization: Top Keywords
    kw_df = pd.DataFrame(word_counts, columns=['word', 'count'])
    plt.figure(figsize=(12, 8))
    sns.barplot(data=kw_df, x='count', y='word', palette='viridis')
    plt.title('Top 20 Keywords in Reviews')
    plt.savefig('plots/top_keywords.png')
    plt.close()
    
    # Product Distribution
    print("\n--- Product Counts ---")
    print(df['product'].value_counts())
    
    # Save a summary report
    with open('analysis_report.md', 'w', encoding='utf-8') as f:
        f.write("# EDA Report: Shopping Reviews\n\n")
        f.write("## Overview\n")
        f.write(f"- Total Reviews: {len(df)}\n")
        f.write(f"- Columns: {', '.join(df.columns)}\n\n")
        
        f.write("## Review Length Distribution\n")
        f.write("![Review Length Distribution](plots/review_length_dist.png)\n\n")
        
        f.write("## Top 20 Keywords\n")
        f.write("![Top Keywords](plots/top_keywords.png)\n\n")
        
        f.write("## Summary Statistics\n")
        f.write("```\n")
        f.write(str(df['content_length'].describe()))
        f.write("\n```\n\n")
        
        f.write("## Key Insights\n")
        f.write("1. Most reviews are relatively concise, with a peak around the median length.\n")
        f.write("2. Dominant keywords include product-related terms (e.g., '노이즈' (noise), '캔슬링' (canceling), '배송' (delivery)).\n")
        f.write("3. Detailed mention of AirPods Pro 2 features suggests high user engagement with tech specs.\n")

if __name__ == "__main__":
    run_eda('shop-review.csv')
