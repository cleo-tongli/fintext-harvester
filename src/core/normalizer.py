import langid, pandas as pd

def normalize_record(rec: dict) -> dict:
    if rec.get("published_at"):
        rec["published_at"] = pd.to_datetime(rec["published_at"], utc=True, errors="coerce").isoformat()
    blob = " ".join([rec.get("title") or "", rec.get("description") or "", rec.get("text") or ""])[:1000]
    rec["language"] = langid.classify(blob)[0] if blob.strip() else None
    return rec
