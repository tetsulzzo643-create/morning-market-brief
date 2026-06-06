"""
collect.py — 市況データ取得モジュール

デフォルトは株価・FX・ニュースを収集する market_data() を返します。
別テーマに差し替えたい場合は下部「テーマ差し替えガイド」を参照してください。
"""
import datetime
import time

import yfinance as yf

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── 取得対象 ──────────────────────────────────────────────────────────────────

INDICES = [
    ("日経平均",   "^N225"),
    ("ダウ",       "^DJI"),
    ("S&P500",    "^GSPC"),
    ("ナスダック", "^IXIC"),
    ("SOX指数",   "^SOX"),
]

FX = [
    ("ドル円",   "USDJPY=X"),
    ("米10年債", "^TNX"),
]

COMMODITIES = [
    ("WTI原油", "CL=F"),
    ("金",      "GC=F"),
    ("BTC",     "BTC-USD"),
]

NEWS_FEEDS = [
    ("NHK",     "https://www3.nhk.or.jp/rss/news/cat6.xml"),
    ("日経",    "https://www.nikkei.com/rss/news.rss"),
    ("Reuters", "https://feeds.reuters.com/reuters/businessNews"),
    ("CNBC",    "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
]


# ── 内部ユーティリティ ────────────────────────────────────────────────────────

def _fetch(symbol: str) -> dict:
    try:
        hist = yf.Ticker(symbol).history(period="5d")
        closes = hist["Close"].dropna().tolist()
        if len(closes) < 2:
            return {}
        price = closes[-1]
        prev  = closes[-2]
        pct   = (price - prev) / prev * 100
        return {"price": round(price, 4), "pct_change": round(pct, 2)}
    except Exception:
        return {}


def _fetch_news(max_per_source: int = 5, total: int = 15) -> list:
    if not (HAS_FEEDPARSER and HAS_REQUESTS):
        return []
    items, seen, result = [], set(), []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MarketBot/1.0)"}
    for src, url in NEWS_FEEDS:
        try:
            r = requests.get(url, timeout=8, headers=headers)
            feed = feedparser.parse(r.text)
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                ts  = time.mktime(pub) if pub else 0
                items.append({"src": src, "title": title, "ts": ts})
        except Exception:
            pass
    for item in sorted(items, key=lambda x: x["ts"], reverse=True):
        if item["title"] not in seen:
            seen.add(item["title"])
            t = (datetime.datetime.fromtimestamp(item["ts"]).strftime("%H:%M")
                 if item["ts"] else "--")
            result.append(f"[{item['src']} {t}] {item['title']}")
            if len(result) >= total:
                break
    return result


# ── メインのデータ取得関数 ────────────────────────────────────────────────────

def market_data() -> str:
    """
    主要市況データとニュースを収集してテキストで返す。
    summarize.py に渡す「生データ文字列」として使われます。
    """
    lines = [f"市況データ取得日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} JST", ""]

    # 主要指数
    lines.append("【主要指数】")
    for name, sym in INDICES:
        d = _fetch(sym)
        if d:
            sign = "+" if d["pct_change"] >= 0 else ""
            lines.append(f"  {name}: {d['price']:,.2f} ({sign}{d['pct_change']:.2f}%)")
        else:
            lines.append(f"  {name}: 取得失敗")

    lines.append("")

    # FX・金利
    lines.append("【FX・金利】")
    for name, sym in FX:
        d = _fetch(sym)
        if d:
            sign = "+" if d["pct_change"] >= 0 else ""
            lines.append(f"  {name}: {d['price']:.4f} ({sign}{d['pct_change']:.2f}%)")
        else:
            lines.append(f"  {name}: 取得失敗")

    lines.append("")

    # コモディティ
    lines.append("【コモディティ】")
    for name, sym in COMMODITIES:
        d = _fetch(sym)
        if d:
            sign = "+" if d["pct_change"] >= 0 else ""
            lines.append(f"  {name}: {d['price']:,.2f} ({sign}{d['pct_change']:.2f}%)")
        else:
            lines.append(f"  {name}: 取得失敗")

    lines.append("")

    # ニュース
    news = _fetch_news()
    if news:
        lines.append("【主要ニュース】")
        for item in news:
            lines.append(f"  {item}")

    return "\n".join(lines)


# ── テーマ差し替えガイド ──────────────────────────────────────────────────────
# 別テーマにする場合は、以下の手順で差し替えてください:
#
# 1. 新しいデータ取得関数を定義する（例: crypto_data, macro_data, etc.）
#    def my_topic_data() -> str:
#        ...
#        return "生データ文字列"
#
# 2. main.py の import を変更する:
#    from src.collect import my_topic_data as collect_data
#
# 例: 仮想通貨特化の場合は COMMODITIES を BTC/ETH/SOL 等に差し替えて
#     INDICES/FX を削除し、NEWS_FEEDS を暗号資産系フィードに変更するだけです。
# ─────────────────────────────────────────────────────────────────────────────
