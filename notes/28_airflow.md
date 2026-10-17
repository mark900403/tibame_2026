# 28 · Airflow（排程與工作流）

> 對應課程：10/15（Airflow 分散式版本 1/2）

## 重點摘要

[apscheduler](21_env_config_scheduler.md) 適合簡單排程；要管理**多個有相依關係的任務**（資料收集→清理→存庫→算指標→視覺化），業界主流是 **Airflow**。它用 **DAG 圖**描述任務關係，有 Web UI、Web Log，GCP/AWS 原生支援。

## 核心觀念

### 1. 為什麼選 Airflow？
- **最多人用**的排程管理工具 → 好找工程師、好維護（冷門工具難維護）。
- 良好的 **Web UI**（延續 Portainer/phpMyAdmin/RabbitMQ 都有 Web UI 的理念）。
- **自動生成架構圖**、良好的 Web Log 介面。
- **GCP、AWS 原生支援**、可擴充（分散式架構）。

### 2. DAG（Directed Acyclic Graph，有向非循環圖）
- 描述系統內**任務彼此之間的關係**（誰先誰後）。
- 「有向」＝有方向（A→B）；「非循環」＝不會繞回來（不能 A→B→A）。
- 例（股票）：`資料收集 → 資料清理 → 存資料庫 → 製作技術指標 → 更新策略 → 存資料庫 → 視覺化`。
- 寫完程式，Airflow **自動生成 DAG 圖**，任務關係一目了然。

## 一、用 Docker Swarm 架設 Airflow

```bash
git clone https://github.com/TibameSam/dataflow.git
docker pull linsamtw/tibame_dataflow:0.0.1      # 或改成你自己的 image
```
事前準備：
1. **初始化 MySQL database**（Airflow 要一個 db 存它的狀態，開 phpMyAdmin 建）。
2. 設定 **Node Labels**（Portainer，[27 章](27_docker_swarm_practice.md)）。
3. 建立 admin 使用者：
   ```bash
   uv run --env-file=.env airflow users create \
     --username admin --firstname lin --lastname sam --role Admin -p admin \
     --email xxx@gmail.com
   ```
4. 部署（Linux/WSL）：
   ```bash
   DOCKER_IMAGE_VERSION=0.0.1 docker stack deploy --with-registry-auth \
     -c docker-compose-airflow.yml airflow
   ```
   > Mac 用 `0.0.1.arm64` 的 image。
5. 開 `http://127.0.0.1:5000`，帳密 `admin / admin`。預設 DAG 是暫停，打開開關即可執行。

## 二、`airflow.cfg` 幾個重要參數

| 參數 | 意義 |
|------|------|
| `dags_folder` | DAG 程式放哪（`/dataflow/dataflow/dags`） |
| `executor = CeleryExecutor` | 用 Celery 分散式執行任務（呼應[14 章](14_distributed_crawler.md)） |
| `sql_alchemy_conn` | Airflow 狀態存哪個 MySQL（`mysql+pymysql://root:密碼@mysql/airflow`） |
| `base_log_folder` | log 放哪 |

> 參數很多，初學只要懂這幾個；其餘查官方文件。

## 三、怎麼寫 DAG？（Airflow 很特別的語法）

```python
# dags/abcd.py（觀念示意）
task_a >> [task_b, task_c] >> task_d      # a 完成後 b、c 平行，兩者都完成後才 d
# 或
task_a >> task_b >> task_c                # 依序執行
```
- 用 `>>` 表示先後相依；寫完 code，Airflow **自動建出 DAG 圖**。

### 資料夾結構（職責分離）
```
dataflow/
├─ dags/     ← 建立 DAG、「管理」任務與相依性
└─ etl/      ← 「實作」任務（爬蟲、上傳資料庫…）
```
- `etl/` 層依需求建不同任務，`dags/` 層統一管理、設相依性。**職責分離**，好維護。

## 四、常見 Operator（任務的種類）

| Operator | 用途 |
|----------|------|
| **BashOperator** | 執行 Bash/Shell 指令（linux 指令/工具） |
| **PythonOperator** | 執行 Python 程式（例如爬蟲任務） |
| **EmptyOperator** | 建立節點/匯合點（例如「爬完所有股票」後才做策略計算） |
| **BranchPythonOperator** | 分支判斷——爬蟲前先 Check 是否該爬（網站是否更新） |
| **DockerOperator** | 用 Docker 容器為基礎執行任務 |

### DockerOperator 的威力與設定
- 同一個 Airflow 底下，不同專案可用**不同 docker image**，不會有 Python 版本/套件衝突。
- 因為 Airflow 本身跑在容器裡，要讓它能在**容器外建 Docker 容器**，需掛載：
  ```yaml
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  ```
  （和 [Portainer agent](26_docker_swarm_intro.md) 同樣的機制：掛 `docker.sock` 才能控制宿主機的 Docker。）

## 整體架構回顧（到這裡你已經走完一條 ETL 產線）
```
Airflow(排程/DAG) ──觸發──▶ Producer ─▶ RabbitMQ ─▶ Worker(爬蟲) ─▶ MySQL
                                                                   │
                                                        API(FastAPI) / Redash(視覺化)
            全部用 Docker Swarm 部署在多台 Node，用 Portainer 管理
```

## 常見錯誤

- **DAG 沒打開開關**：預設暫停，不會執行。
- **DockerOperator 沒掛 `docker.sock`**：Airflow 無法在容器外起 Docker。
- **沒先初始化 Airflow 的 MySQL db**：Airflow 起不來（它要 db 存狀態）。
- **以為 Airflow 取代 Celery**：不是——`CeleryExecutor` 代表 Airflow 底層還是用 Celery 分散式執行。

## 小練習

1. 把兩個任務用 `task_a >> task_b` 串起來，看 Airflow 自動生成的 DAG 圖。
2. 用 `BranchPythonOperator` 寫「若今天網站有更新才爬，否則略過」的分支。
3. 想一想：你的 ETF 專題若用 Airflow，DAG 會長怎樣？（提示：`產生清單 → 抓價 → 寫入MySQL → 算報酬 → 視覺化`）

⬅ 上一章：[27 Docker Swarm 實戰](27_docker_swarm_practice.md) ｜ [名詞小字典](glossary.md) ｜ 回 [課程總覽](../README.md)
