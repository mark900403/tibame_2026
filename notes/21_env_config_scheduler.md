# 21 · 環境管理、資安與排程

> 對應課程：09/17（分散式爬蟲 3）
> 需要套件：`apscheduler==3.10.4`、`loguru==0.6.0`

## 重點摘要

一個專案要能在**開發 / 測試 / 產品**三種環境無痛切換，靠的是把「會變的設定」抽出來（`local.ini` → `.env`），程式只讀環境變數。另外，**帳號密碼等機密絕對不能進 git**。最後用 **apscheduler** 讓爬蟲任務**定時自動執行**。

## 核心觀念

### 1. 三種環境（dev / test / prod）
| 環境 | 用途 |
|------|------|
| **dev（開發）** | 你筆電上開發，連本地的 rabbitmq/mysql（host 多半是 `127.0.0.1`） |
| **test/CI（測試）** | push 到 GitHub 後，GitHub Actions 自動測試 |
| **prod（產品）** | 測試過關 → 包成 docker image + `.env` → 上線 |

### 2. 設定管理：`local.ini` → `.env` → `config.py`
- `local.ini`：寫各環境的設定模板（DEV / DOCKER / PROD）。
- `genenv.py`：依選的環境產生 `.env` 檔。
- `config.py`：程式讀 `.env` 的環境變數。

```bash
ENV=DEV python genenv.py       # 產生 dev 版 .env
ENV=DOCKER python genenv.py    # 產生 docker 版 .env（host 改成服務名稱）
# 程式碼完全不用改，只換 .env
```
- 環境變數慣例：**全域/機密用全大寫**（`MYSQL_HOST`、`RABBITMQ_HOST`），區域變數小寫。
- 這就是為什麼 broker/host 要用**變數**而不是寫死 `127.0.0.1:5672`（[14 章](14_distributed_crawler.md)）——換環境只改 `.env`。

### 3. uv 會自動讀 `.env`（uv 的第二個好處）
```bash
uv run --env-file=.env python test_config.py
```
- `uv`、`pipenv`、`poetry` 可直接讀 `.env` 當環境變數；`python`、`conda`、`colab` 不行。

### 4. 資安：機密**不要進 git**
- `host / user / password / token` 等機密**不寫進 `local.ini`、不進 git**。
- 業界用 **GCP Secret Manager / AWS** 等工具管理機密。
- 外洩真實案例：Uber、Benz、微軟（38TB）都發生過 private repo/機密外洩。
- 核心理念：**相信系統、不要相信人**——所以要 CI/CD 自動化，減少人為疏失。
- 其他防護：用 **docker service name 當 host**（外洩也不知道真實 IP）、用**內網 IP**。
- 面試時講這段，代表你有基本資安概念。

### 5. docker image 版本用環境變數
不想每次改 `docker-compose.yml` 的 image 版本 → 用 `${DOCKER_IMAGE_VERSION}`：
```bash
DOCKER_IMAGE_VERSION=0.0.3 docker compose -f docker-compose-worker-network-version.yml up -d
```
- 指令前綴 `KEY=VALUE`：在 Linux 是「只對這次指令有效的臨時環境變數」。
- 可為不同環境建不同 Dockerfile：`dev.Dockerfile` / `ci.Dockerfile` / `prod.Dockerfile`，build 成 `:0.0.3.dev` / `.ci` / `.prod`。

## 定時排程：apscheduler

### 為什麼用 apscheduler 不用 crontab？
- 可用 **Python 寫排程** → 進 git 做版控；多個 ETL 任務的執行時間一目了然。

### 為什麼用 loguru 不用 print？
- apscheduler 在**背景執行**，`print` 不會顯示；**loguru** 專門顯示 log，背景也看得到。

### scheduler.py（觀念示意）
```python
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
import time

def send_crawler_task():
    logger.info("發送爬蟲任務")     # 用 logger.info 取代 print
    # ... producer 發送任務（把 producer 包成函式）...

scheduler = BackgroundScheduler()
scheduler.add_job(send_crawler_task, "interval", hours=12)  # 每 12 小時一次
scheduler.start()

# 主程式要「持續執行」，否則 python 跑完就結束、排程也關掉
while True:
    time.sleep(10)
```
- **Background 模式**：背景執行，要自己寫 `while + sleep` 撐住主程式。
- **Blocking 模式**（`scheduler_blocking.py`）：用 `BlockingScheduler`，程式會自己持續運作，不用 `while`。

### 排程要 24 小時開機嗎？
要。所以放雲端 VM：
- GCP GCE：最便宜約 $7.1/月（有 $300 免費額度/90 天），但有網路流量費、費用難預估。
- Linode：約 $5/月，含 1TB 流量，費用固定好預估。

## 常見錯誤

- **機密寫進 git**：最嚴重的資安疏失；用 `.env`（且 `.gitignore` 排除）+ Secret Manager。
- **排程用 `print` 看不到輸出**：改用 `loguru`。
- **background 排程沒 `while/sleep`**：程式瞬間結束、排程失效。
- **換環境改程式碼**：應該只換 `.env`，程式讀環境變數就好。
- **直接 `python` 跑卻讀不到 .env**：用 `uv run --env-file=.env`。

## 小練習

1. 寫 `local.ini` 的 DEV 與 DOCKER 兩段，差別只在 host（`127.0.0.1` vs 服務名稱）。
2. 用 apscheduler 寫一個「每 10 秒用 `logger.info` 印一次時間」的排程。
3. 想一想：你的 ETF 專題若要「每天收盤後自動抓價入庫」，排程該設幾點、放哪裡執行？

⬅ 回 [課程總覽](../README.md) ｜ ➡ 下一章：[22 Docker 部署 MySQL](22_docker_mysql_deploy.md)
