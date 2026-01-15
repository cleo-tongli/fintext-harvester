#!/usr/bin/env python
import os, sys, time
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.adapters.api_gdelt import iter_domain_by_day
from src.core.fetcher import get
from src.core.extractor import extract_text
from src.core.normalizer import normalize_record
from src.core.storage import append_jsonl_for_day

DEFAULT_DOMAINS = [
    "cnbc.com","finance.yahoo.com","marketwatch.com","nasdaq.com","nyse.com",
    "ecb.europa.eu","federalreserve.gov","bankofengland.co.uk","boj.or.jp",
    "sec.gov","cftc.gov","bis.org","imf.org",
]

def parse_domains(env): return [d.strip() for d in env.split(",") if d.strip()] if env else DEFAULT_DOMAINS

def main():
    days = int(os.environ.get("GDELT_BACKFILL_DAYS", "30"))
    slices = int(os.environ.get("GDELT_SLICES_PER_DAY", "24"))
    domains = parse_domains(os.environ.get("GDELT_DOMAINS"))

    today = datetime.now(timezone.utc).date()
    grand_total = 0
    for i in range(days):
        day = datetime.combine(today - timedelta(days=i+1), datetime.min.time()).replace(tzinfo=timezone.utc)
        print(f"=== {day.date()} ===")
        day_total = 0
        for domain in domains:
            batch = []
            try:
                for rec in iter_domain_by_day(day, domain, slices_per_day=slices):
                    try:
                        html = get(rec["url"]).content
                        first = html[:6000].lower()
                        rec["paywall"] = rec.get("paywall", False) or (b"subscribe" in first or b"paywall" in first)
                        ext = extract_text(html); rec.update(ext)
                        rec = normalize_record(rec)
                    except Exception:
                        pass  # 保留元数据，方便后续重抓
                    batch.append(rec)
                if batch:
                    append_jsonl_for_day(batch, day.date())
                    print(f"[{day.date()}][{domain}] saved: {len(batch)}")
                    day_total += len(batch)
                else:
                    print(f"[{day.date()}][{domain}] no data")
            except Exception as e:
                print(f"[{day.date()}][{domain}] error: {e}")
            time.sleep(0.2)
        print(f"[{day.date()}] total: {day_total}")
        grand_total += day_total
    print("TOTAL:", grand_total)

if __name__ == "__main__":
    main()
