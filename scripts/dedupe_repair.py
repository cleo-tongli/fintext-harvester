#!/usr/bin/env python
import os, sys
from pathlib import Path
import pandas as pd

MIN_TEXT_CHARS = int(os.getenv("MIN_TEXT_CHARS", "0"))
FILTER_YH_NEWS = os.getenv("FILTER_YH_NEWS", "0") == "1"
DAYS = os.getenv("DEDUPE_DAYS", "").strip()

# 在容器里 /app 是工作目录，这里显式用绝对路径更稳
BRONZE_ROOT = Path("/app/data/bronze")

def list_day_files():
    days = sorted(BRONZE_ROOT.glob("*/docs.jsonl"))
    if not days:
        print("No docs.jsonl found under /app/data/bronze"); sys.exit(0)
    if DAYS == "all": return days
    if DAYS.isdigit(): return days[-int(DAYS):]
    return [days[-1]]

def preferred_order(m):
    order = {"trafilatura":0,"readability":1,"boilerpipe":2,"justext":3,"fallback":9,None:5,"":5}
    return order.get(m, 5)

def load_df(p: Path) -> pd.DataFrame:
    df = pd.read_json(p, lines=True)
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    if "text" in df.columns:
        df["text_len"] = df["text"].fillna("").astype(str).str.len()
    else:
        df["text"] = ""; df["text_len"] = 0
    df["method_rank"] = df.get("extract_method").apply(preferred_order) if "extract_method" in df.columns else 5
    return df

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if FILTER_YH_NEWS and "url" in df.columns:
        df = df[~df["url"].str.contains("finance\\.yahoo\\.com", case=False, na=False) | df["url"].str.contains("/news/", case=False, na=False)]
    if MIN_TEXT_CHARS > 0:
        df = df[df["text_len"] >= MIN_TEXT_CHARS]
    return df

def dedupe_df(df: pd.DataFrame) -> pd.DataFrame:
    cols=[]
    if "method_rank" in df.columns: cols.append("method_rank")
    cols += ["text_len"]
    if "published_at" in df.columns: cols.append("published_at")
    df = df.sort_values(cols, ascending=[True, False, True], na_position="last")
    if "url_hash" in df.columns:
        df = df.drop_duplicates(subset=["url_hash"], keep="first")
    elif "url" in df.columns:
        df = df.drop_duplicates(subset=["url"], keep="first")
    return df

def save_outputs(df: pd.DataFrame, day_dir: Path):
    out_parquet = day_dir / "docs_dedup.parquet"
    out_jsonl   = day_dir / "docs_dedup.jsonl"
    # 直接让 pandas 处理时间序列化（ISO）
    df.to_parquet(out_parquet, index=False)
    df.to_json(out_jsonl, orient="records", lines=True, force_ascii=False, date_format="iso")
    return out_jsonl, out_parquet

def process_one(p: Path):
    day_dir = p.parent
    print(f"=== {day_dir.name} ===")
    src = load_df(p); n0 = len(src)
    by_src0 = src["source_id"].value_counts() if "source_id" in src.columns else None

    df = clean_df(src.copy())
    df = dedupe_df(df); n1 = len(df)

    out_jsonl, out_parquet = save_outputs(df, day_dir)
    print(f"Input: {n0}  →  Deduped: {n1}  (removed: {n0-n1})")
    if by_src0 is not None:
        print("By source (before):"); print(by_src0.to_string())
    if "source_id" in df.columns:
        print("By source (after):"); print(df["source_id"].value_counts().to_string())
    print(f"Saved: {out_jsonl}  &  {out_parquet}\n")

def main():
    for p in list_day_files():
        process_one(p)

if __name__ == "__main__":
    main()
