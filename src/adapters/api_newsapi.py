import os, math, hashlib, time
from datetime import datetime, timedelta, timezone
from typing import Iterable, Dict, Any
import requests
from tenacity import retry, wait_exponential, stop_after_attempt

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")
BASE = "https://newsapi.org/v2/everything"

def _hdr():
    return {"X-Api-Key": NEWSAPI_KEY, "User-Agent": "fintext-harvester/1.0"}

@retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
def _get(params):
    r = requests.get(BASE, headers=_hdr(), params=params, timeout=30)
    if r.status_code == 429:
        raise RuntimeError("NewsAPI rate limit (429)")
    r.raise_for_status()
    return r.json()

def _collect(block):
    for a in block.get("articles", []):
        url = a.get("url") or ""
        yield {
            "url": url,
            "url_hash": hashlib.md5(url.encode()).hexdigest(),
            "title": a.get("title"),
            "description": a.get("description"),
            "published_at": a.get("publishedAt"),
            "source_id": "newsapi_reuters",
            "source_name": "Reuters via NewsAPI",
            "crawl_method": "newsapi",
        }

def _day_range(day_utc: datetime):
    start = day_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    end   = start + timedelta(days=1) - timedelta(seconds=1)
    return start, end

def _fetch_pages(base_params, max_pages, page_size):
    first = _get({**base_params, "page": 1, "pageSize": page_size})
    total = min(first.get("totalResults", 0), max_pages * page_size)
    pages = min(max_pages, math.ceil(total / page_size)) if total else (1 if first.get("articles") else 0)
    yield from _collect(first)
    for p in range(2, pages + 1):
        blk = _get({**base_params, "page": p, "pageSize": page_size})
        yield from _collect(blk)
        time.sleep(0.2)

def iter_reuters_by_day(day_utc: datetime, max_pages=3, page_size=100) -> Iterable[Dict[str, Any]]:
    """
    拉取某个 UTC 日期内的 Reuters 文章；先尝试 sources=reuters，
    若 0 条则降级为 domains=reuters.com。
    """
    if not NEWSAPI_KEY:
        raise RuntimeError("NEWSAPI_KEY is empty")
    start, end = _day_range(day_utc)

    # 尝试 1：sources=reuters
    p1 = dict(
        from_param=start.isoformat(),
        to=end.isoformat(),
        language="en",
        sortBy="publishedAt",
        sources="reuters",
    )
    p1["from"] = p1.pop("from_param")
    items = list(_fetch_pages(p1, max_pages, page_size))
    if items:
        for it in items: yield it
        return

    # 尝试 2：domains=reuters.com
    p2 = dict(
        from_param=start.isoformat(),
        to=end.isoformat(),
        language="en",
        sortBy="publishedAt",
        domains="reuters.com",
    )
    p2["from"] = p2.pop("from_param")
    for it in _fetch_pages(p2, max_pages, page_size):
        yield it
