# 24 · API：FastAPI（Load）

> 對應課程：09/24（API Load 1）
> 需要套件：`fastapi`、`uvicorn`、`sqlalchemy`、`pymysql`、`pandas`、`loguru`

## 重點摘要

資料存進 [MySQL](23_worker_upload_mysql.md) 後，怎麼讓別人（前端、其他工程師、AI）**讀取**？用 **API**。這一步是 ETL 的 **Load（讀取）**。課程用 **FastAPI** 建立 API、讀 MySQL、回傳資料，並包成 Docker 部署。

## 核心觀念

### 1. 什麼是 API？
- **界接介面**：不同程式/軟體之間呼叫、傳遞資料，自由度高。
- **RESTful API**：一種設計規範，定義 `GET`/`POST`/`PUT`/`DELETE` 等操作。
- AI 時代：AI 不用裝任何套件就能呼叫你的 API；任何程式語言都能透過 API 拿到你的資料。

### 2. Flask vs FastAPI
| | Flask | **FastAPI** |
|--|-------|---------|
| 定位 | 輕量 WSGI 框架 | 現代、高效能、基於型別提示 |
| 優點 | 簡單 | **自動產生 API 文件**、支援 async、Pydantic 資料模型 |
| 缺點 | 功能少 | 學習曲線較高 |
| 業界 | 新創 | **永豐、17LIVE、美光** |

> 課程結論：**用 FastAPI，不要再用 Flask**。

## 一、啟動 API

```bash
uv sync
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8888
```
指令拆解：
- `uvicorn`：FastAPI 官方推薦的 web server。
- `api.main:app`：進入點＝`api/main.py` 裡的 `app` 物件。
- `--reload`：程式改動自動重啟（**開發用**）。
- `--host 0.0.0.0`：對所有網卡開放。
- `--port 8888`：對外 port。

### 自動產生的 API 文件（FastAPI 殺手級功能）
- `http://127.0.0.1:8888/docs` → **Swagger UI**（開放原始碼的 API 文件標準介面）。
- `http://127.0.0.1:8888/redoc` → 另一個文件介面。
- 在 `/docs` 可以 **Try it out** → 輸入參數 → 看到 curl、Request URL、Response，等於線上測 API。

## 二、main.py 結構（觀念示意）

```python
from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd

app = FastAPI()                                   # 建立 app 物件（進入點）
engine = create_engine("mysql+pymysql://root:密碼@mysql:3306/mydb")  # 連 MySQL

@app.get("/taiwan_stock_price")                   # 定義一個 GET API 與路徑
def taiwan_stock_price(stock_id: str, start_date: str, end_date: str):
    # 根據輸入參數組 SQL
    sql = f"""
        select * from taiwan_stock_price
        where StockID = '{stock_id}'
          and Date between '{start_date}' and '{end_date}'
    """
    data_df = pd.read_sql(sql, con=engine)        # 送給 MySQL 執行、回傳 DataFrame
    return data_df.to_dict("records")             # ⚠ 回傳必須是 json/dict，不能是 DataFrame
```

重點：
- `@app.get("/路徑")`：把下面的函式註冊成一支 API。
- 參數（`stock_id` 等）會自動變成 API 的查詢參數，並顯示在 Swagger。
- **回傳要 json / dict**（`to_dict("records")`），不能直接回 DataFrame。
- **效能**：對查詢欄位設**主鍵/索引**後，查詢從 0.07 秒 → 0.0005 秒（差很多，呼應 [19 章 Index](19_view_index.md)）。

## 三、包成 Docker 部署

API repo 結構幾乎**照抄 crawler**（readme / uv / pyproject.toml / local.ini / genenv.py / with.env.Dockerfile / docker-compose）：
```bash
docker build -f with.env.Dockerfile -t <你的帳號>/tibame_api:0.0.1 .
docker push <你的帳號>/tibame_api:0.0.1
DOCKER_IMAGE_VERSION=0.0.1 docker compose -f docker-compose-api-network-version.yml up -d
```
- compose 相較 crawler 多了 **`ports`**（因為 API 要跟容器外連線）。
- 服務名稱、image、hostname、command 依 API 調整。

## 開發一個 repo 的「事前準備」（可重用的模板）
每個新 repo 幾乎都需要：`api/crawler 結構` + `README.md` + `uv` + `pyproject.toml` + `local.ini`/`genenv.py` + `Dockerfile` + `docker-compose.yml`。
> 工程師不是只有 coding。準備一份自己的 side project 模板，新 repo 照抄，快速建雛形。

## 常見錯誤

- **回傳 DataFrame**：API 要回 json/dict，用 `df.to_dict("records")`。
- **SQL 直接字串拼接**：有 injection 風險，正式應參數化（[20 章](20_pymysql.md)）。
- **忘了開 `ports`**：API 容器對外連不到。
- **`--reload` 用到正式環境**：`--reload` 只給開發用。
- **DOCKER 環境 host 寫死 127.0.0.1**：用服務名稱 `mysql`。

## 小練習

1. 啟動範例 API，打開 `/docs`，用 Try it out 查一檔股票。
2. 新增一支 `/health` API 回傳 `{"status": "ok"}`。
3. 想一想：你的 ETF 專題若要做「查詢回傳」（[專題指南](../project/README.md)第 7 節），就是用 FastAPI 讀你寫好的 `etf_price` 表 → 回傳 json。

⬅ 上一章：[23 Worker 上傳 MySQL](23_worker_upload_mysql.md) ｜ ➡ 下一章：[25 資料視覺化：Redash](25_redash_visualization.md)
