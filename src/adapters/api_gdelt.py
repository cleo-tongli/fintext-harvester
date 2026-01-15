import hashlib, requests, json
from datetime import datetime, timezone, timedelta
from typing import Iterable, Dict, Any, List
from tenacity import retry, wait_exponential, stop_after_attempt

BASE = "https://api.gdeltproject.org/api/v2/doc/doc"

def _parse_seendate(s: str) -> str | None:
    if not s: return None
    s = s.strip()
    if s.isdigit() and len(s) == 14:
        dt = datetime.strptime(s, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return dt.isoformat()
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc).isoformat()
    except Exception:
        return None

@retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
def _fetch_slice(domain: str, start_dt: datetime, end_dt: datetime, max_records: int = 250) -> List[dict]:
    params = {
        "query": f"domain:{domain}",
        "mode": "artlist",
        "format": "json",
        "sort": "DateAsc",
        "maxrecords": str(max_records),
        "startdatetime": start_dt.strftime("%Y%m%d%H%M%S"),
        "enddatetime":   end_dt.strftime("%Y%m%d%H%M%S"),
    }
    r = requests.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    try:
        j = r.json()
    except json.JSONDecodeError:
        # 偶发脏响应，触发 tenacity 重试
        raise
    items = j.get("articles") or j.get("artlist") or j.get("data") or []
    out = []
    for a in items:
        url = a.get("url") or a.get("link") or ""
        if not url: 
            continue
        pub = _parse_seendate(a.get("seendate") or a.get("date") or a.get("published") or "")
        out.append({
            "url": url,
            "url_hash": hashlib.md5(url.encode()).hexdigest(),
            "title": a.get("title"),
            "description": a.get("title"),
            "published_at": pub,
            "source_id": f"gdelt_{domain.replace('.', '_')}",
            "source_name": f"{domain} via GDELT",
            "crawl_method": "gdelt",
            "language": a.get("language"),
            "paywall": False,
        })
    return out

def iter_domain_by_day(day_utc: datetime, domain: str, slices_per_day: int = 24) -> Iterable[Dict[str, Any]]:
    day_utc = day_utc.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    step = timedelta(hours=max(1, 24 // max(1, slices_per_day)))
    start = day_utc
    end_of_day = day_utc + timedelta(days=1) - timedelta(seconds=1)
    while start <= end_of_day:
        end = min(start + step - timedelta(seconds=1), end_of_day)
        for it in _fetch_slice(domain, start, end):
            yield it
        start += step
