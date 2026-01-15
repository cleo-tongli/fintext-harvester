from src.core.fetcher import get
from src.core.extractor import extract_text
from src.core.normalizer import normalize_record
from src.core.storage import append_jsonl
from typing import List

def run_adapter(adapter) -> int:
    out = []
    for rec in adapter.iter_items():
        try:
            html = get(rec["url"]).content
            # 简单付费墙特征
            first = html[:6000].lower()
            rec["paywall"] = (b"subscribe" in first or b"paywall" in first)
            ext = extract_text(html)
            rec.update(ext)
            rec = normalize_record(rec)
            out.append(rec)
        except Exception as e:
            rec["http_status"] = "error"
            out.append(rec)
    if out:
        append_jsonl(out)
    return len(out)
