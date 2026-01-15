import random, time, requests
from tenacity import retry, wait_exponential, stop_after_attempt

UA_POOL = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 Version/17 Safari/605.1.15"
]

@retry(wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5))
def get(url, timeout=20, headers=None):
    hdrs = {"User-Agent": random.choice(UA_POOL), **(headers or {})}
    resp = requests.get(url, timeout=timeout, headers=hdrs)
    resp.raise_for_status()
    time.sleep(0.3)  # 轻微节流
    return resp
