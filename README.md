# fintext-harvester (media-only)

Pull and clean recent financial news text (CNBC / Yahoo Finance / MarketWatch / Nasdaq) into daily-partitioned JSONL & Parquet files.  
Docker image: `tongliyn/fintext-harvester:latest`  
GitHub: https://github.com/tongli-yn/fintext-harvester

---

## What it does

- Fetches news articles from public sources (via RSS and GDELT domain slices)
- Normalizes fields (url, title, description, published_at, text, source)
- Deduplicates by `url_hash`/`url` and exports:
  - `docs.jsonl` (raw)
  - `docs_dedup.jsonl` and `docs_dedup.parquet` (cleaned)
- Organizes output by day: `data/bronze/YYYY-MM-DD/`

> **Scope:** media sites only (no central bank / regulator feeds).

---

## Quick start (30-day backfill + dedupe)

```bash
docker run --rm --entrypoint /usr/bin/env \
  -e HTTP_PROXY= -e HTTPS_PROXY= -e NO_PROXY= -e http_proxy= -e https_proxy= -e no_proxy= \
  -e GDELT_BACKFILL_DAYS=30 \
  -e GDELT_SLICES_PER_DAY=12 \
  -e GDELT_SLEEP_S=2.0 \
  -e GDELT_SLEEP_JITTER=1.0 \
  -e GDELT_DOMAINS="cnbc.com,finance.yahoo.com,marketwatch.com,nasdaq.com" \
  -e FILTER_YH_NEWS=1 \
  -e MIN_TEXT_CHARS=500 \
  -v "$PWD/data:/app/data" \
  -v "$PWD/logs:/app/logs" \
  tongliyn/fintext-harvester:latest \
  bash -lc "python /app/scripts/backfill_gdelt_domains.py && DEDUPE_DAYS=all python /app/scripts/dedupe_repair.py"

