"""
Yahoo 股市 API：被動式 ETF 股價 / 除權息 / 分割 資料收集
你的專題分工（Extract）。對應課程：05(API+JSON)、06(headers)、07(pandas)、20(PyMySQL)

用法：
    pip install pandas          # 或 uv add pandas
    python etf_fetch.py         # 會抓 SYMBOLS，輸出 3 個 CSV，並印出含息年化報酬

資料來源：Yahoo Finance v8 chart API
    https://query1.finance.yahoo.com/v8/finance/chart/0050.TW?...&events=div,split
    回傳 JSON，含：每日 OHLC/成交量、adjclose(還原價)、dividends(除權息)、splits(分割)
"""
from __future__ import annotations
import json
import time
import datetime as dt
import urllib.request as req
import pandas as pd

# ── 設定（config）─────────────────────────────
SYMBOLS = ["0050.TW", "0056.TW", "006208.TW"]   # 你要追蹤的被動式 ETF（可自行增減）
YEARS = 12                                        # 抓幾年（目標 10 年分析，多抓一點緩衝）
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 Chrome/151 Safari/537.36"}


def fetch_chart(symbol: str, years: int = YEARS) -> dict:
    """打 Yahoo chart API，回傳解析後的 JSON（course 05：urllib + json）。"""
    period2 = int(time.time())
    period1 = period2 - 60 * 60 * 24 * 365 * years
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?period1={period1}&period2={period2}&interval=1d&events=div%2Csplit")
    r = req.Request(url, headers=HEADERS)          # course 06：加 headers 假裝瀏覽器
    content = req.urlopen(r, timeout=30).read()
    return json.loads(content)                     # JSON 字串 → dict


def _ts_to_date(ts: int) -> str:
    """Unix 秒數 → 'YYYY-MM-DD' 字串。"""
    return dt.datetime.fromtimestamp(ts, dt.UTC).date().isoformat()


def parse_prices(symbol: str, data: dict) -> pd.DataFrame:
    """每日股價 → DataFrame（含還原收盤 adj_close）。"""
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    adj = res["indicators"]["adjclose"][0]["adjclose"]
    rows = []
    for i, t in enumerate(ts):
        rows.append({
            "symbol": symbol,
            "date": _ts_to_date(t),
            "open": q["open"][i],
            "high": q["high"][i],
            "low": q["low"][i],
            "close": q["close"][i],        # Yahoo 的 close 通常已還原「分割」
            "adj_close": adj[i],           # 還原「分割 + 除權息」→ 算長期報酬用這個
            "volume": q["volume"][i],
        })
    return pd.DataFrame(rows).dropna(subset=["close"])


def parse_dividends(symbol: str, data: dict) -> pd.DataFrame:
    """除權息紀錄 → DataFrame。"""
    events = data["chart"]["result"][0].get("events", {}).get("dividends", {})
    rows = [{"symbol": symbol, "ex_date": _ts_to_date(d["date"]), "amount": d["amount"]}
            for d in events.values()]
    return (pd.DataFrame(rows).sort_values("ex_date")
            if rows else pd.DataFrame(columns=["symbol", "ex_date", "amount"]))


def parse_splits(symbol: str, data: dict) -> pd.DataFrame:
    """分割紀錄 → DataFrame（台股 ETF 常已還原進 close，故可能為空）。"""
    events = data["chart"]["result"][0].get("events", {}).get("splits", {})
    rows = [{"symbol": symbol, "date": _ts_to_date(s["date"]),
             "numerator": s.get("numerator"), "denominator": s.get("denominator"),
             "ratio": s.get("splitRatio")} for s in events.values()]
    return (pd.DataFrame(rows).sort_values("date")
            if rows else pd.DataFrame(columns=["symbol", "date", "numerator", "denominator", "ratio"]))


def cagr(prices: pd.DataFrame, symbol: str) -> float | None:
    """用還原收盤(adj_close)算「含息年化報酬」CAGR。"""
    d = prices[prices["symbol"] == symbol].sort_values("date")
    if len(d) < 2:
        return None
    start, end = d["adj_close"].iloc[0], d["adj_close"].iloc[-1]
    years = (pd.to_datetime(d["date"].iloc[-1]) - pd.to_datetime(d["date"].iloc[0])).days / 365
    return (end / start) ** (1 / years) - 1


def main():
    all_prices, all_divs, all_splits = [], [], []
    for sym in SYMBOLS:
        print(f"抓取 {sym} ...")
        data = fetch_chart(sym)
        all_prices.append(parse_prices(sym, data))
        all_divs.append(parse_dividends(sym, data))
        all_splits.append(parse_splits(sym, data))
        time.sleep(1)                              # 禮貌：放慢，避免被擋（course 05/06）

    prices = pd.concat(all_prices, ignore_index=True)   # course 07：concat 合併
    divs = pd.concat(all_divs, ignore_index=True)
    splits = pd.concat(all_splits, ignore_index=True)

    prices.to_csv("etf_price.csv", index=False, encoding="utf-8")
    divs.to_csv("etf_dividend.csv", index=False, encoding="utf-8")
    splits.to_csv("etf_split.csv", index=False, encoding="utf-8")

    print(f"\n完成：price={len(prices)} 列, dividend={len(divs)} 列, split={len(splits)} 列")
    print("\n各 ETF 期間含息年化報酬(CAGR)：")
    for sym in SYMBOLS:
        c = cagr(prices, sym)
        if c is not None:
            print(f"  {sym}: {c*100:.2f}% /年（含息還原）")


if __name__ == "__main__":
    main()
