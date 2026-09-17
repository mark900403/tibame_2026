"""
把抓到的 ETF 資料寫進 MySQL（三張表都寫）。
對應課程：17(交易 commit/rollback)、20(PyMySQL 參數化查詢)

用法：
    pip install pymysql pandas            # 或 uv add pymysql pandas
    # 先建表：mysql 裡 SOURCE schema.sql
    # 連線資訊用環境變數（不要把密碼寫死在程式裡）
    export MYSQL_HOST=localhost MYSQL_USER=root MYSQL_PASSWORD=你的密碼 MYSQL_DB=etf
    python etf_to_mysql.py
"""
from __future__ import annotations
import os
import pymysql
from etf_fetch_pro import (STOCK_IDS, fetch_chart,
                           parse_prices, parse_dividends, parse_splits)

# ── 連線設定：從環境變數讀，避免把密碼寫死（course 20 安全提醒）──
DB_CONFIG = dict(
    host=os.environ.get("MYSQL_HOST", "localhost"),
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
    # 團隊價格表欄位：date, stock_id, adj_close（date 是保留字，用反引號）
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
    total_p = total_d = total_s = 0
    for sid in STOCK_IDS:
        print(f"抓取並寫入 {sid} ...")
        data = fetch_chart(sid)
        total_p += save_prices(parse_prices(sid, data))
        total_d += save_dividends(parse_dividends(sid, data))
        total_s += save_splits(parse_splits(sid, data))
    print(f"完成：price {total_p} 列、dividend {total_d} 列、split {total_s} 列 已寫入 MySQL")


if __name__ == "__main__":
    main()
