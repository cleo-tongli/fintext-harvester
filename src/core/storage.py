
import os, json, pandas as pd
from datetime import datetime, timezone, date

def _bucket_dir(root="data/bronze"):
    d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = os.path.join(root, d); os.makedirs(path, exist_ok=True); return path

def _bucket_dir_for(day: date, root="data/bronze"):
    d = day.strftime("%Y-%m-%d")
    path = os.path.join(root, d); os.makedirs(path, exist_ok=True); return path

def append_jsonl(records, root="data/bronze", fname="docs.jsonl"):
    path = os.path.join(_bucket_dir(root), fname)
    with open(path, "a", encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    return path

def append_jsonl_for_day(records, day: date, root="data/bronze", fname="docs.jsonl"):
    path = os.path.join(_bucket_dir_for(day, root), fname)
    with open(path, "a", encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r, ensure_ascii=False)+"\n")
    return path

