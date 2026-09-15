# 14 · 分散式爬蟲：RabbitMQ + Celery + Flower

> 對應課程：09/12、09/14
> 目標：懂分散式爬蟲的角色分工，會用 Docker 啟動 RabbitMQ/Flower，用 Celery 發任務、多工人平行處理。

## 重點摘要

一次要爬 2000 支股票、1000 篇文章，用 `for` 迴圈一個個做太慢。**分散式**的做法是：一個「主管」把任務丟進「傳遞中心」，很多「工人」同時來拿任務、平行執行。學會這套，你可以「一次控制 10 台電腦跑爬蟲」。

## 核心觀念：三個角色

```
Producer(主管) ──發任務──▶  RabbitMQ(Broker 傳遞中心)  ◀──拿任務── Worker×N(工人)
   producer.py                    ▲ 監控                        worker.py (celery)
                                 Flower
```

| 角色 | 是誰 | 做什麼 |
|------|------|--------|
| **Producer 主管** | Python (`producer.py`) | 發派爬蟲任務 |
| **Broker 傳遞中心** | **RabbitMQ** | 收 Producer 的任務、轉發給 Worker |
| **Worker 工人** | Python + **Celery** (`worker.py`) | 從 Broker 拿任務、執行爬蟲、存資料庫 |
| **Flower 監控** | 網頁儀表板 | 即時看有幾個工人、任務狀態 |

- 為什麼要拆成「發任務」與「執行任務」兩支 Python？→ 這樣**執行的工人可以有很多個、同時做**，而且可以分散在不同機器/IP（還能避免爬太快被 ban IP）。
- 類似的 Broker 還有 Redis、Kafka、GCP Pub/Sub，概念相同，會一種就好。

## 一、用 Docker 啟動 RabbitMQ 與 Flower

先取得課程專案並同步環境（見 [11 Git](11_linux_git.md)、[13 uv](13_uv_python_env.md)）：
```bash
git clone https://github.com/TibameSam/crawler
cd crawler/
code .
uv sync
```

啟動服務（**游標要在 crawler 資料夾**）：
```bash
docker compose -f rabbitmq.yml up -d     # 啟動 RabbitMQ + Flower
docker compose -f rabbitmq.yml down      # 關閉
docker ps                                # 看容器（記住名稱，如 crawler-rabbitmq-1）
docker logs crawler-rabbitmq-1           # 看 log
```

用網頁確認：
- **RabbitMQ 管理頁**：<http://127.0.0.1:15672/>（帳號/密碼：`worker` / `worker`）。
- **Flower 監控頁**：<http://127.0.0.1:5555/>（一開始還沒有工人）。

> `rabbitmq.yml` 裡定義了兩個服務（rabbitmq、flower），各自的 image、port、環境變數（帳密/host），且 flower 要等 rabbitmq 起來後再啟動。細節見 [12 Docker 的 compose 段](12_docker.md)。

## 二、Celery：發任務與啟動工人

**Celery** 是別人寫好的 Python 工具，讓你簡單地發任務、收任務。

### 發送任務（Producer）
```bash
uv run python crawler/producer.py        # 送出任務到 RabbitMQ
```
### 啟動工人（Worker）
```bash
uv run celery -A crawler.worker worker --loglevel=info
```
指令拆解：
- `celery`：執行 celery。
- `-A crawler.worker`：告訴 celery「程式碼在哪」（crawler 資料夾下的 worker.py）。
- `worker`：啟動「工人」模式。
- `--loglevel=info`：印出 info 等級的 log（還有 warning/debug/error）。

工人啟動後會**收到任務 → 執行爬蟲**，到 Flower（:5555）就看得到這個工人。按 `Ctrl + C` 讓工人「下班」。

### 多個工人（要取不同名字）
```bash
# 開多個終端機，各自取不同 -n 名稱
uv run celery -A crawler.worker worker -n worker1 --loglevel=info
uv run celery -A crawler.worker worker -n worker2 --loglevel=info
```
- `-n`（`--hostname`）：指定工人名稱；**不同工人要不同名字**，否則在 Flower 不會分開顯示。
- 開 N 個終端機 = N 倍效能；開 N 台電腦跑 worker = 用 N 台電腦同時做。**這就是分散式**。
- 用 `htop` 看 CPU/記憶體，還沒用滿就可以再加工人。

## 三、多佇列（Queue）：不同網站分不同生產線（09/14）

**MQ = Message Queue（訊息佇列）**。可以把任務丟到**不同佇列**，讓不同網站的爬蟲**同時進行、互不阻塞**（例：證交所 twse、櫃買 tpex 分開跑，避免頻繁訪問單一站被 ban）。

```bash
# 發送到不同 queue（例：twse、tpex）
uv run python crawler/producer_multi_queue_print.py

# 預設 producer.py 會送到名為 "celery" 的預設佇列
uv run python crawler/producer.py
```
到 RabbitMQ 管理頁會看到 `twse`、`tpex`（或 `celery`）等佇列。

工人**指定只接哪些佇列**：
```bash
uv run celery -A crawler.worker worker -Q twse,tpex --loglevel=info
# -Q twse,tpex：這個工人只接收 twse 和 tpex 佇列的任務（可 1 個或多個，逗號分隔）
```
> 預設工人只接 `celery` 佇列；要接別的佇列一定要加 `-Q`。

清理佇列：在 RabbitMQ 管理頁進入某佇列，最下方 **Purge**（清空任務）或 **Delete**（刪除整個佇列）。

## 四、定義任務（tasks）

工人能執行的「任務」要用 Celery 的裝飾器註冊：
```python
# tasks.py（觀念示意）
from .worker import app

@app.task()               # 用 @app.task() 把函式註冊成「可被派發的任務」
def crawler_twse(...):
    # 這裡放你的爬蟲程式（把課程的 print("crawler") 換成真正爬蟲）
    ...
```
- `config.py` 裡的 `broker` 指向 RabbitMQ 的位置；用**大寫環境變數** `RABBITMQ_HOST`，方便本地/雲端切換（本地連 `127.0.0.1`，雲端/容器連服務名稱 `rabbitmq`）。
- 課程把 `tasks_crawler_finmind.py` 當範例，回家作業就是**把裡面換成你自己的專題爬蟲**。

## 五、全部搬進 Docker：worker/producer 容器化（09/14）

把爬蟲打包成 image（見 [12 Docker](12_docker.md) 的 Dockerfile / build / push），再用 compose 啟動 worker/producer 容器。**重點是 network**：

```bash
# 讓 rabbitmq 與 worker 在同一個內網，才能用「服務名稱」互連
docker network create my_network

docker compose -f rabbitmq-network.yml up -d              # RabbitMQ/Flower（external network）
docker compose -f docker-compose-worker-network.yml up -d # 工人容器
docker logs crawler-crawler_twse-1                        # 確認不再 Connection refused

# 發送任務（producer 容器）
docker compose -f docker-compose-producer-network.yml up -d
docker logs -f crawler-producer_multi_queue-1
```
- **常見錯誤**：worker 容器連 `127.0.0.1:5672` → `Connection refused`。因為容器內的 `127.0.0.1` 是它自己。解法：同一個 `my_network` + host 改成服務名稱 `rabbitmq`。
- 改了程式要**重新 build image**（版本 +1，如 `0.0.2`），compose 裡的 image 版本也要一起改。

## 業界怎麼用（為什麼值得學）
- 旅遊新創：分散式爬 50 家旅行社商品做比價。
- 證券：`order` 佇列派 50 工人下單、`data` 佇列派 10 工人查歷史股價，互不影響。
- 17LIVE：每分鐘更新 1 萬用戶推薦，分散 20 台 VM（甚至有 GPU）。
- 好處：**擴展效能**、**多 IP 避免被 ban**、**單機故障仍可運作**、**成本更低**。

## 常見錯誤

- **工人沒出現在 Flower** → 多工人要用 `-n` 取不同名字。
- **工人收不到某佇列任務** → 預設只接 `celery` 佇列，要加 `-Q 佇列名`。
- **容器間 Connection refused** → 同一 docker network + 服務名稱當 host（不要 `127.0.0.1`）。
- **指令在錯的資料夾執行** → docker/uv 指令要在 `crawler` 專案資料夾內。
- **改了程式忘了 rebuild image** → 容器仍跑舊版；重 build 並更新版本號。

## 小練習

1. `docker compose -f rabbitmq.yml up -d` 後，打開 :15672 與 :5555 兩個網頁確認服務。
2. 開兩個終端機各啟一個 `-n worker1`、`-n worker2`，到 Flower 看是否出現兩個工人。
3. 想一想：你的專題若要爬 3 個不同網站，應該設幾個佇列？工人怎麼分配 `-Q`？

⬅ 上一章：[13 uv：Python 環境管理](13_uv_python_env.md) ｜ [名詞小字典](glossary.md) ｜ [專題步驟指南](../PROJECT_GUIDE.md)
