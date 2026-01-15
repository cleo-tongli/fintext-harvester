#!/usr/bin/env python
import os, sys, yaml
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.pipeline import run_adapter
from src.adapters.rss_generic import RSSAdapter

def main():
    cfg = yaml.safe_load(open("config/sources.yaml","r",encoding="utf-8"))
    total = 0
    for s in cfg["rss_sources"]:
        adapter = RSSAdapter(s["url"], s["id"], s["name"])
        n = run_adapter(adapter)
        print(f"[DONE] {s['id']} -> {n} docs")
        total += n
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
