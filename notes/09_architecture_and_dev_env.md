# 09 · 架構圖與開發環境總覽

> 對應課程：09/07（架構圖）
> 這是課程「第二部分」的開場：從「會寫爬蟲」進化到「像工程師一樣做一個資料系統」。

## 重點摘要

這一段課程開始把你從「單機寫程式」帶到「**資料工程（Data Engineering）**」的世界：先用**架構圖**把整個系統畫出來，再逐步把每個元件（爬蟲、訊息佇列、資料庫、API、排程）實作出來。老師強調一句話：**「環境設定，是所有 Python 初學者的痛」**——所以這部分先把工具環境打好。

## 核心觀念

### 1. 為什麼要先畫架構圖？
架構圖 = 系統的「地圖」。它讓你（和團隊）一眼看懂：資料**從哪來 → 經過哪些元件 → 到哪去**。先有藍圖，再蓋房子。

- 工具：[draw.io / diagrams.net](https://app.diagrams.net/)（免費、可存到 GitHub）。
- 版本演進：先畫 **V0/V1 最簡單版**，隨課程加入新工具再持續 update。
- 課程建議先放個人 GitHub repo，之後專題再放團隊 repo。

### 2. 課程的目標架構（大地圖）
整門課會一塊一塊拼出這張圖：

```
                     ┌─────────────┐
   Producer(主管) ──▶│  RabbitMQ   │◀── 監控: Flower
   發送爬蟲任務       │ (訊息佇列)   │
                     └──────┬──────┘
                            │ 拿任務
                   ┌────────▼────────┐
                   │ Crawler/Worker  │  多個工人平行爬蟲
                   │   (Python)      │
                   └────────┬────────┘
                            │ 存資料
                        ┌───▼────┐      ┌──────┐
                        │ MySQL  │────▶│  API │──▶ 使用者
                        └───┬────┘      └──────┘
                            │
                        ┌───▼─────┐
                        │ Redash  │  Dashboard 視覺化
                        └─────────┘

   Airflow(排程) ──▶ 定時觸發 Producer / Crawler
```

各區塊對應：
- **分散式爬蟲**：Producer → RabbitMQ / Flower → Crawler（[第 14 章](14_distributed_crawler.md)）。
- **API**：Crawler → MySQL → API。
- **Dashboard**：Crawler → MySQL → Redash。
- **Scheduler**：Airflow → Crawler / Producer（定時自動跑）。

> 這門「資料處理」課的主線就是：**Extract（收集）→ 存資料庫 → 提供 API/視覺化 → 用排程自動化**。你現在在「Extract」這一段的工程化。

### 3. 需要哪些工具、為什麼
| 工具 | 角色 | 為什麼 |
|------|------|--------|
| WSL / Ubuntu | Linux 環境 | 業界服務都跑在 Linux（GCP/AWS 雲端機都是 Linux） |
| VSCode | 開發工具(IDE) | 一個介面搞定 Python + git + docker + linux |
| Git / GitHub | 版本控制 | 記錄、協作、之後接 CI/CD |
| Docker | 容器 | 解決「我電腦能跑、別人不能跑」的環境問題 |
| uv | Python 環境管理 | 快、統一管理 Python 與套件版本 |
| RabbitMQ / Celery / Flower | 分散式 | 用多台/多程序同時爬，大幅加速 |

各工具的實作分別在：[10 WSL/VSCode](10_wsl_vscode.md)、[11 Linux/Git](11_linux_git.md)、[12 Docker](12_docker.md)、[13 uv](13_uv_python_env.md)、[14 分散式爬蟲](14_distributed_crawler.md)。

## 動手做：畫你的第一張架構圖

1. 打開 [app.diagrams.net](https://app.diagrams.net/)，選擇存到 **GitHub**（授權讀寫指定 repo）。
2. 先在 GitHub 建一個 repo 放架構圖，檔名標 `v0`。
3. 畫出你專題的最小版本：`爬蟲 → 資料庫 → API/視覺化`。
4. 之後每學一個新元件（RabbitMQ、MySQL、Airflow…）就回來更新，命名 `v1`、`v2`…。

> 小技巧：AI 也能根據你的程式碼幫你畫架構圖，前提是**程式碼本身要有清楚的架構**。

## 常見誤解

- **「架構圖是浪費時間」**：相反，先畫圖能避免亂寫、方便團隊溝通，也是面試時展示系統思維的利器。
- **「一次要畫到完美」**：不用。先 V0 最小可用，再迭代。
- **「這些工具好多、好難」**：它們是分工合作的一套流程，後面章節會一個個帶你裝起來。

## 小練習

1. 用 draw.io 畫出你專題目前的 `爬蟲 → CSV/資料庫 → 圖表` 流程（V0）。
2. 對照大地圖，標出你的專題「現在做到哪一塊、下一塊要做什麼」。

⬅ 回 [課程總覽](../README.md) ｜ ➡ 下一章：[10 WSL 與 VSCode 設定](10_wsl_vscode.md)
