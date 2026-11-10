"""Built-in product catalog: load, filter by budget, rank by keyword match."""
import json
import re
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


def load_catalog(path=None):
    with open(path or DEFAULT_CATALOG, encoding="utf-8") as f:
        return json.load(f)["products"]


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def search(products, parsed, limit=3):
    """Rank products by keyword overlap, filtered by budget.

    Each parsed keyword token is weighted by inverse document frequency:
    a token that appears in few products (e.g. "headphones") counts more
    than a generic one (e.g. "wireless"). Score: +3 * idf per token matching
    the product's name/keywords, +1 * idf per token matching its description.
    The parsed category adds a flat +1 bonus when it overlaps the product's
    category. Budget is a hard filter when present. Ties break toward the
    lower price.
    """
    import math

    budget = parsed.get("budget_usd")
    kw_tokens = set()
    for kw in parsed.get("keywords") or []:
        kw_tokens |= _tokens(kw)
    cat_tokens = _tokens(parsed.get("category"))

    # Document frequency of every token across the catalog (name + keywords
    # + description + category), for IDF weighting.
    n = len(products)
    df = {}
    for p in products:
        toks = (_tokens(p["name"]) | _tokens(" ".join(p.get("keywords", [])))
                | _tokens(p["description"]) | _tokens(p["category"]))
        for t in toks:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((n + 1) / (df.get(t, 0) + 1)) + 1 for t in kw_tokens}

    scored = []
    for p in products:
        if budget is not None and p["price"] > float(budget):
            continue
        name_kw = _tokens(p["name"]) | _tokens(" ".join(p.get("keywords", [])))
        desc = _tokens(p["description"])
        score = sum(3 * idf[t] for t in kw_tokens & name_kw)
        score += sum(1 * idf[t] for t in kw_tokens & desc)
        if cat_tokens and (cat_tokens & _tokens(p["category"])):
            score += 1
        # Require at least one real keyword hit when keywords were given.
        if kw_tokens and not (kw_tokens & name_kw) and not (kw_tokens & desc):
            continue
        scored.append((score, -p["price"], p))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [p for _, _, p in scored[:limit]]
