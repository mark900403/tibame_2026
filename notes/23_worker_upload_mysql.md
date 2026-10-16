# 23 · Worker 上傳 MySQL 與自動去重（Transform）

> 對應課程：09/21（MySQL Transform 2）
> 需要套件：`sqlalchemy`、`pymysql`

## 重點摘要

把[分散式爬蟲](14_distributed_crawler.md)抓到的資料，透過 **SQLAlchemy + PyMySQL** 上傳到 [MySQL](22_docker_mysql_deploy.md)，並用**主鍵自動去重**（重複上傳只保留最新一筆）。這一步完成了 ETL 的 **Transform（清理、儲存）**。

## 核心觀念：ETL

| 階段 | 做什麼 | 課程 |
|------|--------|------|
| **Extract 提取** | 收集資料（爬蟲） | [05–08](05_web_crawling_api_json.md)、[14](14_distributed_crawler.md) |
| **Transform 轉換** | 清理、存進資料庫 | 本章 |
| **Load 載入/讀取** | 提供 API 讀取 | [24](24_api_fastapi.md) |

## 一、上傳資料到 MySQL（SQLAlchemy + pandas）

```python
import pandas as pd
from sqlalchemy import create_engine

# 連線字串：mysql+pymysql://帳號:密碼@host:port/資料庫
engine = create_engine("mysql+pymysql://root:密碼@127.0.0.1:3306/mydb")

df = pd.DataFrame(...)                 # 爬蟲抓到的資料轉成 DataFrame
df.to_sql("TaiwanStockPrice", con=engine,
          if_exists="append",         # ⚠ append = 新增（不要用 replace，會蓋掉整張表）
          index=False)
```
- `create_engine(連線字串)`：建立與 MySQL 的連線（SQLAlchemy）。
- `df.to_sql(表名, engine, if_exists="append", index=False)`：把 DataFrame **一次寫入** MySQL。
- 執行：`uv run python crawler/upload_data_to_mysql.py`，回 phpMyAdmin 就看到資料。

### JSON → DataFrame
有些爬蟲抓回來是 JSON（在 Python 是 dict），要先轉 DataFrame：
```python
df = pd.DataFrame([json_data])   # 注意：單筆 dict 要先包成 list [json_data]
```

### 結合爬蟲
把原本 `tasks.py` 裡的 `print("upload db")` 改成 `upload_data_to_mysql(df)`，工人爬完就自動上傳資料庫。

## 二、自動去重（重複上傳不報錯、只留最新）

直接 `to_sql(append)` 遇到重複會卡主鍵。用 SQLAlchemy 的 upsert 處理：**設了 primary key 才會去重**。

```python
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.mysql import insert

engine = create_engine("mysql+pymysql://root:密碼@127.0.0.1:3306/mydb")
metadata = MetaData()
table = Table("TaiwanStockPrice", metadata, autoload_with=engine)

def upsert(df):
    rows = df.to_dict("records")
    stmt = insert(table).values(rows)
    # 主鍵重複時 → 更新成新值（保留最後一筆）
    update = {c.name: stmt.inserted[c.name] for c in table.columns}
    stmt = stmt.on_duplicate_key_update(**update)
    with engine.begin() as conn:
        conn.execute(stmt)
```
- **一定要有 primary key**（如 `stock_id + date`）才會去重。
- 重複（例：`stock_id, date` 相同但 `price` 不同）→ **保留最後一筆、最新的**。
- 應用：PTT 文章用「標題+作者+日期」當主鍵，文章內文更新時自動覆蓋成最新。
- 好處：同學多次發送爬蟲任務、重跑，**都不會出現 error**。

> 這和[第 16/20 章](16_dml.md)的 `INSERT ... ON DUPLICATE KEY UPDATE` 是同一個概念，只是改用 SQLAlchemy 寫。

## 三、結合分散式 + Docker

1. `local.ini` 除了 rabbitmq，也要設 **mysql** 的 DEV / DOCKER 設定（[21 章](21_env_config_scheduler.md)）。
   - DOCKER 環境的 `MYSQL_HOST` 用**服務名稱 `mysql`**（和 rabbitmq 概念相同）。
2. `config.py` 加入 MySQL 設定（並給預設值，預設用 DEV）。
3. 改完程式要**重新 build image**（版本 +1）、push、用 `docker compose`/swarm 重新部署 worker。
4. 最終流程：`producer 發任務 → rabbitmq → worker 爬蟲 → 上傳 MySQL（自動去重）`。

## 常見錯誤

- **`if_exists="replace"`**：會**刪掉整張表**重建！要用 `append`。
- **單筆 dict 沒包成 list**：`pd.DataFrame(json_data)` 會出錯，要 `pd.DataFrame([json_data])`。
- **沒設主鍵卻想去重**：去重不會生效，或重複資料塞爆。
- **DOCKER 環境 host 寫 127.0.0.1**：容器內連不到，要用服務名稱 `mysql`。
- **改了程式忘了 rebuild image**：容器仍跑舊版。

## 小練習

1. 用 `to_sql(append)` 把一個 3 欄 DataFrame 寫進 MySQL，再去 phpMyAdmin 確認。
2. 對同一主鍵塞兩次不同值，驗證「只保留最後一筆」。
3. 把你 ETF 專題的 `etf_to_mysql.py`（[project](../project/README.md)）對照本章——你用的 `ON DUPLICATE KEY UPDATE` 正是這裡的去重概念。

⬅ 上一章：[22 Docker 部署 MySQL](22_docker_mysql_deploy.md) ｜ ➡ 下一章：[24 API：FastAPI](24_api_fastapi.md)
