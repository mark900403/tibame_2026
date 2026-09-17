# 專題分工：被動式 ETF 資料收集（Yahoo 股市 API）

> 你的任務：用 Yahoo 股市 API 查詢**被動式 ETF** 的**股價**、**分割紀錄**、**除權息**資料。
> 專題報告目標：透過 ETF 選股，**10 年後有能力購買六都房產**。
> 本文把「你這一段」拆成可執行的程式步驟，並標注用到課程哪一章。

---

## 1. 你在整個專題的位置（架構定位）

對照課程大架構（[notes/09](../notes/09_architecture_and_dev_env.md)）：

```
[你負責] Yahoo API 抓 ETF 資料 ──▶ 清理成表格(pandas) ──▶ 存進 MySQL
                                                              │
                          選股/回測組 ── 讀 MySQL ──▶ 分析報酬、模擬 10 年 ──▶ 報告組：能否買六都房
```

**你是「Extract（資料收集）+ 入庫」這一棒**：把乾淨、可信、可查詢的資料交給後面選股/回測的組員。你交付的品質，決定整份報告的地基。

用到的課程章節：
- [05 API 與 JSON](../notes/05_web_crawling_api_json.md)：用 `urllib` 打 API、`json.loads` 解析。
- [06 headers](../notes/06_html_beautifulsoup.md)：加 `User-Agent` 避免被擋。
- [07 pandas](../notes/07_pandas.md)：整理成 DataFrame、`concat`、存 CSV。
- [15–20 MySQL / PyMySQL](../notes/15_sql_mysql_intro.md)：建表、寫入資料庫。
- [13 uv](../notes/13_uv_python_env.md) / [12 Docker](../notes/12_docker.md) / [14 分散式](../notes/14_distributed_crawler.md)：工程化（選讀）。

---

## 2. 資料來源：Yahoo Finance v8 chart API（已實測可用）

一個網址就能一次拿到「股價 + 除權息 + 分割」：

```
https://query1.finance.yahoo.com/v8/finance/chart/0050.TW
    ?period1=<起始 Unix 秒>&period2=<結束 Unix 秒>
    &interval=1d          # 1d=日線（也可 1wk, 1mo）
    &events=div,split      # 一併回傳 除權息(div) 與 分割(split)
```

- 台股代號格式：**`0050.TW`**（上市）、上櫃是 `.TWO`。
- 回傳 JSON 的重點路徑：
  - 日期：`chart.result[0].timestamp[]`（Unix 秒）
  - 股價：`chart.result[0].indicators.quote[0].{open,high,low,close,volume}[]`
  - **還原收盤**：`chart.result[0].indicators.adjclose[0].adjclose[]`
  - **除權息**：`chart.result[0].events.dividends` → 每筆 `{date, amount}`
  - **分割**：`chart.result[0].events.splits` → 每筆 `{date, numerator, denominator, splitRatio}`

> 實測（本專案 `etf_fetch.py`）：`0050.TW / 0056.TW / 006208.TW` 12 年共 8,763 筆日價、68 筆除權息。
> ⚠ **分割**：台股 ETF 的分割 Yahoo 多半已「還原」進 `close`，所以 `events.splits` 常是空的（美股如 AAPL 才會列出 `4:1`）。這不是程式錯，是資料特性——詳見第 5 節。

> 替代方案：也可用 `yfinance` 套件（`pip install yfinance`，`yf.Ticker("0050.TW").history(period="10y", auto_adjust=False)`）一次拿到 OHLC+Dividends+Splits。但**課程教的是自己打 API+解析 JSON**，所以本專案用原生 `urllib`（更貼合課程、也更懂原理）。

---

## 3. 要收集哪些資料（三張表）

**團隊定案：價格表欄位為 `date, stock_id, adj_close`**（用還原收盤算 10 年報酬）。

| 表 | 內容 | 欄位 |
|----|------|------|
| `etf_price` | 每日還原收盤 | **`date`, `stock_id`, `adj_close`** |
| `etf_dividend` | 除權息（輔助） | stock_id, ex_date, amount |
| `etf_split` | 分割（輔助） | stock_id, split_date, numerator, denominator, ratio |

- **`stock_id`** 存純代號（如 `0050`）；打 API 時再自動補市場後綴（上市 `.TW`、上櫃 `.TWO`）。
- 主鍵設 `(stock_id, date)`，可避免同一檔同一天重複寫入。
- 建表 SQL 在 [`schema.sql`](schema.sql)（對應 [notes/15、16、19](../notes/15_sql_mysql_intro.md)）。
- 價格表只留 `adj_close`（長期報酬只需要它）；若之後想加 OHLC/volume，[`etf_fetch.py`](etf_fetch.py) 裡加欄位即可。

---

## 4. 程式架構（模組化）與實作步驟

抓取程式在 [`etf_fetch.py`](etf_fetch.py)（已實跑通過）。結構：

```
fetch_chart(stock_id) # 打 API、回傳 JSON            (course 05,06)
parse_prices(...)     # JSON → date/stock_id/adj_close (course 07)
parse_dividends(...)  # JSON → 除權息 DataFrame
parse_splits(...)     # JSON → 分割 DataFrame
cagr(...)             # 用 adj_close 算含息年化報酬
main()                # 迴圈多檔、concat、存 CSV
```

### 建議的實作順序（先會動，再擴大）
1. **最小可行**：先抓「一檔 0050、一段期間」，`print` 出前幾筆，確認 JSON 路徑對（[05 章的『先抓一頁成功』精神](../notes/05_web_crawling_api_json.md)）。
2. **轉表格**：把價格/除權息/分割各做成一個 DataFrame（[07 章](../notes/07_pandas.md)）。
3. **多檔迴圈**：用 `for stock_id in STOCK_IDS` 抓多檔，`pd.concat` 合併；每檔間 `time.sleep(1)` 放慢（禮貌、避免被擋）。
4. **存檔**：先存 CSV 當備份，再進 MySQL（下一節）。
5. **每日更新**：之後可用排程（Airflow）每天只抓「新的一天」，避免重抓。

執行（本 repo 已附 `pyproject.toml`，用 uv 一鍵安裝——course 13）：
```bash
uv sync                                  # 依 pyproject.toml/uv.lock 裝好 pandas、pymysql
uv run python project/etf_fetch.py       # 產生 etf_price.csv / etf_dividend.csv / etf_split.csv
```
> 也可用傳統方式：`python -m venv .venv && source .venv/bin/activate && pip install pandas`。

---

## 5. 關鍵觀念：close vs adj_close（一定要懂，否則報酬會算錯）

- **`close`（收盤價）**：當天的實際成交收盤（Yahoo 通常已針對「分割」back-adjust）。
- **`adj_close`（還原收盤）**：把**分割 + 除權息**都還原後的價格。

> 為什麼重要？ETF 每次「除息」股價會往下掉（把配息發給你了），若只看 `close` 會**低估**長期報酬。要算「**含息**的真實報酬」，**一律用 `adj_close`**。

含息年化報酬（CAGR）：
```
CAGR = (期末 adj_close / 期初 adj_close) ^ (1/年數) − 1
```
本專案實測（近 12 年，僅供理解方法，**非未來保證**）：
- `0050.TW` ≈ 21%/年、`006208.TW` ≈ 21%/年、`0056.TW` ≈ 14%/年。

> ⚠ 這數字受近年大多頭影響偏高。做 10 年報告時，建議**另用保守假設**（例如 5%~8%）跑一組，並揭露假設。分割紀錄（`etf_split`）雖然台股多半已還原，仍要收集並在報告中說明「已用還原價，故不重複調整」。

---

## 6. 存進 MySQL（PyMySQL，對應 [notes/20](../notes/20_pymysql.md)）

完整入庫程式在 [`etf_to_mysql.py`](etf_to_mysql.py)：**三張表（價格、除權息、分割）都會寫入**。連線資訊用環境變數（不要把密碼寫死）：
```bash
mysql etf < schema.sql        # 先建表
export MYSQL_HOST=localhost MYSQL_USER=你的帳號 MYSQL_PASSWORD=你的密碼 MYSQL_DB=etf
python etf_to_mysql.py        # 抓取並寫入三張表
```
> 已本機用 MariaDB 實測：3 檔寫入 price 8,763 / dividend 68 / split 0 列；**重跑具冪等性**（`ON DUPLICATE KEY UPDATE`，不會爆主鍵、筆數不變）。

核心寫法：用參數化查詢批次寫入，`INSERT ... ON DUPLICATE KEY UPDATE` 做「有就更新、沒有就新增」：

```python
import pymysql

def get_conn():
    return pymysql.connect(host="localhost", user="root", password="你的密碼",
                           database="etf", charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor)

def save_prices(df):
    # 欄位對齊資料庫：date, stock_id, adj_close（date 是保留字，用反引號）
    sql = """
        insert into etf_price (`date`, stock_id, adj_close)
        values (%(date)s, %(stock_id)s, %(adj_close)s)
        on duplicate key update adj_close = values(adj_close)
    """
    rows = df.where(df.notna(), None).to_dict("records")   # NaN → None
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)   # 批次寫入，比一筆筆快很多
            conn.commit()                    # 異動一定要 commit（course 17/20）
    except Exception:
        conn.rollback()
        raise
```
> `etf_dividend`、`etf_split` 同理，各有 `save_dividends()` / `save_splits()`（見 [`etf_to_mysql.py`](etf_to_mysql.py)）。**參數化**（`%(key)s`）不要用字串拼接（防 SQL Injection）。

---

## 7. 銜接報告目標：10 年後買六都房的試算

你交付資料後，選股/回測組會做這類計算（你也可以先幫忙跑一版，讓報告有數字）：

設你每月定期定額投入 `m` 元、年化報酬 `r`、投資 `n` 個月，月報酬 `i = r/12`：

```
定期定額終值  FV = m × [ ((1+i)^n − 1) / i ]
一次投入終值  FV = P × (1 + r)^10
```

反推「要達成目標房價/頭期款，每月需投入多少」：
```python
def monthly_needed(target, annual_return, years=10):
    i = annual_return / 12
    n = years * 12
    return target * i / ((1 + i)**n - 1)

# 例：目標頭期款 300 萬、假設年化 7%
print(monthly_needed(3_000_000, 0.07))   # ≈ 每月 17,300 元左右
# 例：目標全額 1,500 萬、假設年化 7%
print(monthly_needed(15_000_000, 0.07))  # ≈ 每月 86,000 元左右
```

報告可以這樣呈現：**「若選 0050，用保守 7% 年化，每月投入 X 元，10 年後可累積到六都某區的頭期款/全額」**，並用你收集的**真實歷史資料**做回測佐證（不同進場時間、含息 vs 不含息的差異）。

> 建議在報告揭露：房價數據來源（可另抓內政部實價登錄/六都房價指數）、報酬假設、以及「過去績效不代表未來」的風險說明。

---

## 8. 選讀：把它工程化 / 分散式

- 追蹤**很多檔** ETF 時，可把「每檔抓取」做成一個 Celery 任務，用 RabbitMQ 分派、多工人平行抓（[notes/14](../notes/14_distributed_crawler.md)）。
- 用 `uv` 管理套件（[notes/13](../notes/13_uv_python_env.md)）、包成 Docker image 部署（[notes/12](../notes/12_docker.md)）。
- 用排程每天自動更新（課程後續的 Airflow）。
- 對報告來說這些非必須，但寫進架構圖會很加分。

---

## 9. 注意事項與常見錯誤

- **被擋 / 無回應**：一定要帶 `User-Agent`（[06 章](../notes/06_html_beautifulsoup.md)）；多檔之間 `time.sleep()`；失敗要能重試。
- **報酬算錯**：長期報酬用 `adj_close`，不要用 `close`（見第 5 節）。
- **時間欄位**：API 給的是 Unix 秒，要轉成日期；注意時區（台股用當地日期即可）。
- **缺值 NaN**：非交易日或停牌會有 `None`；寫入 MySQL 前把 `NaN → None`。
- **重複寫入**：主鍵 `(symbol, 日期)` + `ON DUPLICATE KEY UPDATE`，每天重跑才不會爆。
- **分割為空是正常**：台股 ETF 多已還原；仍要收集並在報告註明。
- **合法與禮貌**：Yahoo 資料僅供學習/報告用途，放慢請求、不要大量高頻抓取。

---

## 10. 你的交付介面（跟組員說好）

你最後交出的東西建議是：
1. 三張 MySQL 表（`etf_price` / `etf_dividend` / `etf_split`）+ 一份 `schema.sql`。
2. 一份「資料字典」：每欄意義、單位、更新頻率、資料期間。
3. `etf_fetch.py` 抓取程式（可重跑更新）。
4. （可選）一個 `cagr()` / 報酬試算的小工具，方便回測組直接用。

有了明確介面，選股組讀你的表就能直接做選股與 10 年模擬。

---

### 檔案
- [`etf_fetch.py`](etf_fetch.py)：抓取 + 解析 + 存 CSV（已實測）。
- [`etf_to_mysql.py`](etf_to_mysql.py)：寫入 MySQL 三張表（已用 MariaDB 實測、冪等）。
- [`schema.sql`](schema.sql)：MySQL 三張表定義。

⬅ 回 [課程總覽](../README.md) ｜ 相關：[05 API](../notes/05_web_crawling_api_json.md)、[07 pandas](../notes/07_pandas.md)、[20 PyMySQL](../notes/20_pymysql.md)、[專題步驟指南](../PROJECT_GUIDE.md)
