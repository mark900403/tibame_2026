# 資料處理課程 — 複習筆記與專題指南

這是把 [Elwing-Chou/tibame_20260714](https://github.com/Elwing-Chou/tibame_20260714) 這門「資料處理」課程整理成的**新手友善**複習教材。內容依「主題」重新編排（不是按上課日期），讓你複習時可以一個觀念一個觀念地看。

> 給新手的話：不用怕，這份筆記假設你「完全沒寫過程式」。每個名詞都會用白話解釋，每段程式碼都會逐行說明，並附上常見錯誤與小練習。

## 這門課在學什麼？（一句話）

**「用 Python 把網路上的資料抓下來 → 整理乾淨 → 做成表格分析」**，先把 Python 基本功打好，再進入**資料工程（Data Engineering）**：用 Linux/Docker/分散式架構把爬蟲工程化。

## 學習地圖（建議照順序看）

### 第一部分：Python 與資料處理基本功

| # | 主題 | 你會學到 | 筆記 |
|---|------|----------|------|
| 01 | Python 基礎 | 變數、`print`、`if`、迴圈、函式、柯拉茲猜想 | [notes/01_python_basics.md](notes/01_python_basics.md) |
| 02 | 遞迴與動態規劃(DP) | 什麼是遞迴、終止條件、用「記錄」加速 | [notes/02_recursion_dp.md](notes/02_recursion_dp.md) |
| 03 | 資料結構 | list / dict / set / tuple、雙層 list | [notes/03_data_structures.md](notes/03_data_structures.md) |
| 04 | pygame 小遊戲 | 用「翻牌遊戲」把前面觀念綜合應用 | [notes/04_pygame_game.md](notes/04_pygame_game.md) |
| 05 | 爬蟲：API 與 JSON | 用程式抓網路資料、`urllib`、`json` | [notes/05_web_crawling_api_json.md](notes/05_web_crawling_api_json.md) |
| 06 | HTML 與 BeautifulSoup | 看懂網頁結構、`find`/`find_all`、CSS 選擇器 | [notes/06_html_beautifulsoup.md](notes/06_html_beautifulsoup.md) |
| 07 | pandas 資料處理 | DataFrame、讀寫 CSV、過濾、轉換 `apply` | [notes/07_pandas.md](notes/07_pandas.md) |
| 08 | Selenium 動態爬蟲 | 讓程式「操作瀏覽器」抓需要登入/JS 的網站 | [notes/08_selenium.md](notes/08_selenium.md) |

### 第二部分：工程化與資料工程（環境、Docker、分散式）

| # | 主題 | 你會學到 | 筆記 |
|---|------|----------|------|
| 09 | 架構圖與開發環境總覽 | draw.io 畫架構、整體系統藍圖 | [notes/09_architecture_and_dev_env.md](notes/09_architecture_and_dev_env.md) |
| 10 | WSL 與 VSCode 設定 | 裝 Linux(Ubuntu)、VSCode 連 WSL、必備插件 | [notes/10_wsl_vscode.md](notes/10_wsl_vscode.md) |
| 11 | Linux 指令與 Git | `cd`/`ls`/`mkdir`、git add/commit/push/pull | [notes/11_linux_git.md](notes/11_linux_git.md) |
| 12 | Docker | image/container/volume、compose、Dockerfile、network | [notes/12_docker.md](notes/12_docker.md) |
| 13 | uv：Python 環境管理 | 獨立環境、`uv add`/`sync`/`run`、lock 檔 | [notes/13_uv_python_env.md](notes/13_uv_python_env.md) |
| 14 | 分散式爬蟲 | RabbitMQ + Celery + Flower、多工人/多佇列 | [notes/14_distributed_crawler.md](notes/14_distributed_crawler.md) |

### 工具

| # | 主題 | 內容 | 連結 |
|---|------|------|------|
| ✎ | 名詞小字典 | 全課程關鍵名詞白話速查 | [notes/glossary.md](notes/glossary.md) |
| ★ | 專題步驟指南 | 從 0 做出一個完整資料處理專題 | [PROJECT_GUIDE.md](PROJECT_GUIDE.md) |

## 怎麼跑這些程式？（環境）

課程原本用 **Google Colab**（線上版 Jupyter Notebook，副檔名 `.ipynb`），你不用安裝任何東西，開瀏覽器登入 Google 就能寫。

- 標準 Python 檔案是 `.py`；Colab/Jupyter 的筆記本是 `.ipynb`，可以「一格一格」執行、還能寫筆記(Markdown)。
- 要在自己電腦跑，安裝 Python 後用 `pip install` 安裝套件即可（每篇筆記會標注需要哪些套件）。

## 每篇筆記的固定結構

1. **重點摘要** — 這章在幹嘛、為什麼重要
2. **核心觀念** — 白話 + 比喻
3. **程式範例（逐行說明）** — 對照課程實際的 code
4. **常見錯誤** — 新手最容易踩的雷
5. **小練習** — 確認自己有沒有懂

開始吧 → [notes/01_python_basics.md](notes/01_python_basics.md)
