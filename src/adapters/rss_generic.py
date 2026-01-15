import hashlib, datetime as dt, feedparser
from typing import Iterable, Dict, Any
from .base import BaseAdapter
from src.core.fetcher import get  # 关键：带UA/重试的请求

class RSSAdapter(BaseAdapter):
    def __init__(self, feed_url: str, source_id: str, source_name: str):
        self.feed_url = feed_url
        self.source_id = source_id
        self.source_name = source_name

    def iter_items(self) -> Iterable[Dict[str, Any]]:
        # 先下载（带UA/重试/可跟随跳转），再把字节交给 feedparser
        resp = get(self.feed_url)
        feed = feedparser.parse(resp.content)
        for e in feed.entries:
            url = e.get("link")
            yield {
                "url": url,
                "url_hash": hashlib.md5((url or "").encode()).hexdigest(),
                "title": e.get("title"),
                "description": e.get("summary"),
                "published_at": self._parse_dt(e),
                "source_id": self.source_id,
                "source_name": self.source_name,
                "crawl_method": "rss"
            }

    def _parse_dt(self, e):
        if "published_parsed" in e and e.published_parsed:
            return dt.datetime(*e.published_parsed[:6], tzinfo=dt.timezone.utc).isoformat()
        return None
