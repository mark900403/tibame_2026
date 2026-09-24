"""
把「被動式 ETF」的股價 / 除權息 / 分割 寫進 MySQL（三張表都寫）。
流程：etf_universe(全台股→ETF→被動式) → 逐檔 Yahoo 抓價(依市場給後綴) → 寫入 MySQL
對應課程：12(Docker)、17(交易 commit/rollback)、20(PyMySQL 參數化查詢)

用法：
    uv sync                               # 裝好 pandas、pymysql
    mysql etf < project/schema.sql        # 先建表
    export MYSQL_HOST=localhost MYSQL_USER=你的帳號 MYSQL_PASSWORD=你的密碼 MYSQL_DB=etf
    # 可選：只跑前 N 檔測試 → export ETF_LIMIT=5
    uv run python project/etf_to_mysql.py
"""
from __future__ import annotations
import os
import time
import pymysql
from etf_fetch_pro import (fetch_chart, parse_prices, parse_dividends, parse_splits)
from etf_universe import get_passive_etf_list

# ── 連線設定：從環境變數讀，避免把密碼寫死（course 20 安全提醒）──
DB_CONFIG = dict(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    port=int(os.environ.get("MYSQL_PORT", "3306")),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASSWORD", ""),
    database=os.environ.get("MYSQL_DB", "etf"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


def get_conn() -> pymysql.connections.Connection:
    return pymysql.connect(**DB_CONFIG)


def _save(df, sql: str) -> int:
    """共用寫入：批次 upsert + 交易保護（course 17/20）。回傳寫入列數。"""
    if df is None or df.empty:
        return 0
    rows = df.where(df.notna(), None).to_dict("records")   # NaN → None
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)     # 批次寫入，比一筆筆快很多
            conn.commit()                      # 異動一定要 commit
        return len(rows)
    except Exception:
        conn.rollback()                        # 出錯就還原，避免寫一半
        raise


def save_prices(df) -> int:
    sql = """
        insert into etf_price (`date`, stock_id, adj_close)
        values (%(date)s, %(stock_id)s, %(adj_close)s)
        on duplicate key update adj_close = values(adj_close)
    """
    return _save(df, sql)


def save_dividends(df) -> int:
    sql = """
        insert into etf_dividend (stock_id, ex_date, amount)
        values (%(stock_id)s, %(ex_date)s, %(amount)s)
        on duplicate key update amount = values(amount)
    """
    return _save(df, sql)


def save_splits(df) -> int:
    sql = """
        insert into etf_split (stock_id, split_date, numerator, denominator, ratio)
        values (%(stock_id)s, %(split_date)s, %(numerator)s, %(denominator)s, %(ratio)s)
        on duplicate key update
            numerator = values(numerator),
            denominator = values(denominator),
            ratio = values(ratio)
    """
    return _save(df, sql)


def main():
    etfs = get_passive_etf_list()          # [{stock_id, stock_name, market}, ...]

    limit = os.environ.get("ETF_LIMIT")    # 測試時可只跑前 N 檔
    if limit:
        etfs = etfs[:int(limit)]

    print(f"準備寫入 {len(etfs)} 檔被動式 ETF 到 MySQL ...")
    total_p = total_d = total_s = 0
    failed = []

    for i, e in enumerate(etfs, start=1):
        sid = e["stock_id"]
        market = e["market"]
        try:
            data = fetch_chart(sid, market)            # 依市場給 .TW / .TWO
            total_p += save_prices(parse_prices(sid, data))
            total_d += save_dividends(parse_dividends(sid, data))
            total_s += save_splits(parse_splits(sid, data))
        except Exception as err:
            failed.append(sid)                          # 單檔失敗不中斷整批
            print(f"  ⚠ {sid} 失敗：{str(err)[:60]}")
        time.sleep(1)                                   # 禮貌：放慢，避免被擋
        if i % 20 == 0:
            print(f"  進度 {i}/{len(etfs)} ...")

    print(f"\n完成：price {total_p} 列、dividend {total_d} 列、split {total_s} 列 已寫入 MySQL")
    if failed:
        print(f"失敗 {len(failed)} 檔：{failed}")


if __name__ == "__main__":
    main()
