import hashlib, json, re
import trafilatura
from readability import Document
from bs4 import BeautifulSoup

def _clean_text(txt: str) -> str:
    txt = re.sub(r"\s+", " ", txt or "").strip()
    return txt

def _from_json_ld(html: bytes) -> str | None:
    # 抓取 JSON-LD 里的 Article/articleBody（Yahoo 常见）
    soup = BeautifulSoup(html, "lxml")
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(s.string or "")
            # 可能是列表或单个对象
            items = data if isinstance(data, list) else [data]
            for it in items:
                t = it.get("@type") or it.get("@context")
                if (t and ("Article" in str(t) or "NewsArticle" in str(t))) or it.get("articleBody"):
                    body = it.get("articleBody") or ""
                    if body and len(body) > 80:
                        return _clean_text(body)
        except Exception:
            continue
    return None

def _from_common_selectors(html: bytes) -> str | None:
    # 一些常见容器（包括 Yahoo 的 caas-body）
    soup = BeautifulSoup(html, "lxml")
    candidates = [
        ("div", {"class": re.compile(r"(caas-body|article-body|story-content)")} ),
        ("article", {}),
        ("div", {"itemprop": "articleBody"}),
    ]
    for tag, attrs in candidates:
        node = soup.find(tag, attrs=attrs)
        if node:
            text = node.get_text(separator=" ").strip()
            if len(text) > 80:
                return _clean_text(text)
    return None

def extract_text(html: bytes) -> dict:
    # 1) trafilatura 试一次
    txt = trafilatura.extract(html, include_comments=False, include_tables=False)
    method = "trafilatura"
    if txt and len(txt) >= 200:
        return _pack(txt, method)

    # 2) JSON-LD 抽取（很多“动态站”会把全文放进 JSON-LD）
    txt = _from_json_ld(html)
    if txt:
        return _pack(txt, "json-ld")

    # 3) 常见选择器（Yahoo: .caas-body 等）
    txt = _from_common_selectors(html)
    if txt:
        return _pack(txt, "css-selectors")

    # 4) readability 兜底
    try:
        doc = Document(html)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, "lxml")
        txt = soup.get_text(separator=" ").strip()
        if len(txt) > 80:
            return _pack(_clean_text(txt), "readability")
    except Exception:
        pass

    # 5) 实在不行，返回空
    return _pack("", "none")

def _pack(txt: str, method: str) -> dict:
    return {
        "text": txt,
        "content_hash": hashlib.md5(txt.encode()).hexdigest() if txt else None,
        "extract_method": method
    }
