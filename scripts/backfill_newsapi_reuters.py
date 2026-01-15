#!/usr/bin/env python
import os, sys, time
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.adapters.api_newsapi import iter_reuters_by_day
from src.core.fetcher import get
from src.core.extractor import extract_text
from src.core.normalizer import normalize_record
from src.core.storage import append_jsonl_for_day

def main(days=30, max_pages=3):

    today = datetime.now(timezone.utc).date()
    start_day = today - timedelta(days=1)
    end_day = start_day - timedelta(days=days-1)

    total = 0
    day = start_day
    while day >= end_day:
        day_dt = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
        print(f"=== {day} ===")
        out = []
        try:
            for rec in iter_reuters_by_day(day_dt, max_pages=max_pages):
                try:
                    html = get(rec["url"]).content
                    first = html[:6000].lower()
                    rec["paywall"] = (b"subscribe" in first or b"paywall" in first)
                    ext = extract_text(html)
                    rec.update(ext)
                    rec = normalize_record(rec)
                    out.append(rec)
                except Exception:
                    rec["http_status"] = "error"
                    out.append(rec)
            if out:
                append_jsonl_for_day(out, day)
                total += len(out)
                print(f"[{day}] saved: {len(out)}")
            else:
                print(f"[{day}] no data")
        except Exception as e:
            print(f"[{day}] error: {e}")

            break
        time.sleep(0.5)  # 礼貌节流
        day -= timedelta(days=1)

    print("TOTAL:", total)

if __name__ == "__main__":
    days = int(os.environ.get("NEWSAPI_BACKFILL_DAYS", "30"))
    max_pages = int(os.environ.get("NEWSAPI_MAX_PAGES_PER_DAY", "3"))
    main(days=days, max_pages=max_pages)
