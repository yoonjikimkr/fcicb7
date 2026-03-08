"""
iHerb Sleep 카테고리 – 데이터 수집 & EDA
- scraper.py 가 수집한 SQLite DB를 읽어와 분석
- 성분 태깅, 성분군별 요약, CSV 저장
"""

import os
import re
import sqlite3

import pandas as pd

# ── 경로 설정 ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "iherb_sleep.db")


def load_from_db() -> pd.DataFrame:
    """SQLite DB에서 제품 데이터를 로드"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM iherb_sleep_products", conn)
    conn.close()

    if df.empty:
        raise ValueError("DB에 데이터가 없습니다. 먼저 scraper.py 를 실행하세요.")

    print(f"✅ DB에서 {len(df)}개 제품 로드 완료")
    return df


# ── 주요 성분 태깅 (Rule-based) ──
ACTIVES_MAP = {
    "melatonin": ["멜라토닌", "melatonin"],
    "magnesium": ["마그네슘", "magnesium"],
    "5-htp": ["5-htp", "5 htp", "5htp"],
    "tryptophan": ["트립토판", "tryptophan"],
    "valerian": ["발레리안", "쥐오줌풀", "valerian"],
    "passion_flower": ["패션플라워", "시계꽃", "passion flower", "passionflower"],
    "chamomile": ["카모마일", "캐모마일", "chamomile"],
    "kava": ["카바", "kava"],
    "gaba": ["가바", "gaba"],
    "theanine": ["테아닌", "theanine"],
    "ashwagandha": ["아슈와간다", "ashwagandha"],
    "glycine": ["글리신", "glycine"],
    "lemon_balm": ["레몬밤", "레몬 밤", "lemon balm"],
}


def tag_actives(text: str) -> str | None:
    """제품명에서 주요 성분 키워드를 추출 (우선순위 반영)"""
    text_lower = (text or "").lower()
    found = []
    # ACTIVES_MAP의 순서대로 순회하므로, 마그네슘이 글리신보다 앞에 있으면 우선권을 갖습니다.
    for active_key, keywords in ACTIVES_MAP.items():
        if any(kw in text_lower for kw in keywords):
            found.append(active_key)
    
    # 정렬(sorted)을 제거하여 마그네슘+글리신 제품이 글리신으로 분류되는 것 방지
    return ", ".join(found) if found else None


def first_active(x: str | None) -> str:
    """첫 번째 주성분을 반환 (카테고리 분류용)"""
    if not isinstance(x, str) or not x:
        return "기타/복합"
    # 첫 번째 성분을 주성분으로 보되, '복합제' 키워드가 있다면 필터링 로직 추가 가능
    return x.split(",")[0].strip()


def analyze(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """성분 태깅 + 성분군별 요약 통계"""
    # 제품명 기반 성분 태깅
    df["active_ingredients"] = df["product_name"].apply(tag_actives)
    df["main_active"] = df["active_ingredients"].apply(first_active)

    # 성분군별 요약
    summary = (
        df.groupby("main_active")
        .agg(
            n_products=("product_name", "nunique"),
            avg_price=("price", "mean"),
            med_price=("price", "median"),
            avg_rating=("rating", "mean"),
            avg_reviews=("review_count", "mean"),
            total_reviews=("review_count", "sum"),
        )
        .reset_index()
        .sort_values("n_products", ascending=False)
    )

    return df, summary


def main():
    # 1) DB에서 데이터 로드
    df = load_from_db()

    # 2) 분석
    df_enriched, summary = analyze(df)

    # 3) 결과 출력
    print("\n" + "=" * 60)
    print("📊 성분군별 요약 통계")
    print("=" * 60)
    print(summary.to_string(index=False))

    print("\n" + "=" * 60)
    print("📋 전체 데이터 샘플 (상위 10개)")
    print("=" * 60)
    cols = ["product_name", "brand", "price", "rating", "review_count", "main_active"]
    print(df_enriched[cols].head(10).to_string(index=False))

    # 4) CSV 저장
    os.makedirs(DATA_DIR, exist_ok=True)
    detail_path = os.path.join(DATA_DIR, "iherb_sleep_products_detailed.csv")
    summary_path = os.path.join(DATA_DIR, "iherb_sleep_summary_by_active.csv")

    df_enriched.to_csv(detail_path, index=False, encoding="utf-8-sig")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print(f"\n💾 상세 데이터 저장: {detail_path}")
    print(f"💾 성분 요약 저장:  {summary_path}")

    return df_enriched, summary


if __name__ == "__main__":
    main()
