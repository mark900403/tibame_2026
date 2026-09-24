"""
Yahoo 股市 API：被動式 ETF 資料收集（Extract）
團隊資料庫價格表欄位：date, stock_id, adj_close
另收集 除權息 / 分割 兩張輔助表。
對應課程：05(API+JSON)、06(headers)、07(pandas)、20(PyMySQL)

用法：
    pip install pandas          # 或 uv add pandas
    python etf_fetch_pro.py     # 抓 STOCK_IDS，輸出 CSV，並印出含息年化報酬(CAGR)
"""
from __future__ import annotations
import json
import time
import datetime as dt
import urllib.request as req
import pandas as pd

# ── 設定（config）─────────────────────────────
STOCK_IDS = ["0050", "0056", "006208"]            # 只放純代號；API 會自動補 .TW
MARKET_SUFFIX = ".TW"                              # 上市=.TW，上櫃=.TWO
YEARS = 12                                          # 抓幾年（目標 10 年分析，多抓緩衝）
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 Chrome/151 Safari/537.36"}


def market_suffix(market: str) -> str:
    """上市(twse) → .TW；上櫃(tpex) → .TWO（很多債券 ETF 在上櫃）。"""
    return ".TW" if market == "twse" else ".TWO"


def fetch_chart(stock_id: str, market: str = "twse", years: int = YEARS) -> dict:
    """打 Yahoo chart API，回傳解析後的 JSON（course 05：urllib + json）。"""
    symbol = f"{stock_id}{market_suffix(market)}"  # 0050+twse → 0050.TW；00679B+tpex → 00679B.TWO
    period2 = int(time.time())
    period1 = period2 - 60 * 60 * 24 * 365 * years
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1={period1}&period2={period2}&interval=1d&events=div%2Csplit")
    r = req.Request(url, headers=HEADERS)          # course 06：加 headers 假裝瀏覽器
    return json.loads(req.urlopen(r, timeout=30).read())


def _ts_to_date(ts: int) -> str:
    """Unix 秒數 → 'YYYY-MM-DD' 字串。"""
    return dt.datetime.fromtimestamp(ts, dt.UTC).date().isoformat()


def parse_prices(stock_id: str, data: dict) -> pd.DataFrame:
    """每日還原收盤 → DataFrame，欄位對齊資料庫：date, stock_id, adj_close。"""
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    adj = res["indicators"]["adjclose"][0]["adjclose"]   # 還原收盤（分割+除權息）
    rows = [{"date": _ts_to_date(t), "stock_id": stock_id, "adj_close": adj[i]}
            for i, t in enumerate(ts)]
    return pd.DataFrame(rows).dropna(subset=["adj_close"])


def parse_dividends(stock_id: str, data: dict) -> pd.DataFrame:
    """除權息紀錄 → DataFrame（輔助表）。"""
    events = data["chart"]["result"][0].get("events", {}).get("dividends", {})
    rows = [{"stock_id": stock_id, "ex_date": _ts_to_date(d["date"]), "amount": d["amount"]}
            for d in events.values()]
    return (pd.DataFrame(rows).sort_values("ex_date")
            if rows else pd.DataFrame(columns=["stock_id", "ex_date", "amount"]))


def parse_splits(stock_id: str, data: dict) -> pd.DataFrame:
    """分割紀錄 → DataFrame（台股 ETF 常已還原進價格，故可能為空）。"""
    events = data["chart"]["result"][0].get("events", {}).get("splits", {})
    rows = [{"stock_id": stock_id, "split_date": _ts_to_date(s["date"]),
             "numerator": s.get("numerator"), "denominator": s.get("denominator"),
             "ratio": s.get("splitRatio")} for s in events.values()]
    return (pd.DataFrame(rows).sort_values("split_date")
            if rows else pd.DataFrame(columns=["stock_id", "split_date", "numerator", "denominator", "ratio"]))


def cagr(prices: pd.DataFrame, stock_id: str) -> float | None:
    """用還原收盤(adj_close)算「含息年化報酬」CAGR。"""
    d = prices[prices["stock_id"] == stock_id].sort_values("date")
    if len(d) < 2:
        return None
    start, end = d["adj_close"].iloc[0], d["adj_close"].iloc[-1]
    years = (pd.to_datetime(d["date"].iloc[-1]) - pd.to_datetime(d["date"].iloc[0])).days / 365
    return (end / start) ** (1 / years) - 1


def main():
    all_prices, all_divs, all_splits = [], [], []
    for sid in STOCK_IDS:
        print(f"抓取 {sid} ...")
        data = fetch_chart(sid)
        all_prices.append(parse_prices(sid, data))
        all_divs.append(parse_dividends(sid, data))
        all_splits.append(parse_splits(sid, data))
        time.sleep(1)                              # 禮貌：放慢，避免被擋（course 05/06）

    prices = pd.concat(all_prices, ignore_index=True)   # course 07：concat 合併
    divs = pd.concat(all_divs, ignore_index=True)
    splits = pd.concat(all_splits, ignore_index=True)

    # 價格表欄位順序對齊資料庫：date, stock_id, adj_close
    prices = prices[["date", "stock_id", "adj_close"]]
    prices.to_csv("etf_price.csv", index=False, encoding="utf-8")
    divs.to_csv("etf_dividend.csv", index=False, encoding="utf-8")
    splits.to_csv("etf_split.csv", index=False, encoding="utf-8")

    print(f"\n完成：price={len(prices)} 列, dividend={len(divs)} 列, split={len(splits)} 列")
    print("\n各 ETF 期間含息年化報酬(CAGR)：")
    for sid in STOCK_IDS:
        c = cagr(prices, sid)
        if c is not None:
            print(f"  {sid}: {c*100:.2f}% /年（含息還原）")


if __name__ == "__main__":
    main()
