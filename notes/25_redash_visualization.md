# 25 · 資料視覺化：Redash

> 對應課程：10/03（資料視覺化）

## 重點摘要

資料進了 [MySQL](23_worker_upload_mysql.md) 後，用 **Redash**（免費開源視覺化工具）連資料庫、寫 SQL、做出互動式 **Dashboard**，給非工程師同事看。這是把資料「變成洞察」的最後一哩。

## 核心觀念

### 為什麼不用 Python 畫圖就好？
- Python 畫圖是給自己看；**Redash 內建網站功能**，可直接提供視覺化網頁給非工程師（業務、營運）看，不用自己寫前端。
- Redash 特色：連多種資料庫（MySQL/PostgreSQL/BigQuery…）、寫 SQL 查詢、豐富圖表。
- 類似工具：**Superset**（更強大）、**Grafana**（系統監控專用）。

## 一、用 Docker 啟動 Redash + 連 MySQL

```bash
git clone https://github.com/TibameSam/services.git
docker compose -f docker-compose-redash-local.yml up -d
# 瀏覽器開 http://localhost:5005/ → 設定 Name/Email/Password/Organization → Setup
```

連 MySQL（Data Sources）：
- Host：**`mysql`**（docker 用服務名稱連線）
- Port：`3306`、User：`root`、Password：你的密碼、Database：你的 db

## 二、建立 Query（寫 SQL）

```sql
SELECT StockID, Date, Close, TradeVolume
FROM `taiwan_stock_price`
WHERE StockID = '2330'
```
- 欄位可用 `as` 改中文顯示：`Close as "收盤價"`。
- 建圖：**Add Visualization → Chart → Line**，X 軸選 `Date`、Y 軸選 `Close`/`TradeVolume`，設 Series/顏色 → **Save**。

### 下拉式選單（參數化 Query）
1. 另建一個 Query 列出所有股票代碼：
   ```sql
   SELECT DISTINCT StockID FROM `taiwan_stock_price`
   ```
2. 把主 Query 的 `'2330'` 改成 `'{{股票代碼}}'` → 出現參數。
3. 點齒輪 → 選 **Query Based** → 選剛建立的股票代碼 Query → 變成**下拉式選單**。
4. 日期區間：`AND Date BETWEEN "{{日期.start}}" AND "{{日期.end}}"` → 齒輪選 **Date Range**。

### 紅K綠K（用 `if` 拆欄位）
```sql
SELECT
  Date as "日期",
  Close as "收盤價",
  if(`Change` >= 0, TradeVolume, 0) as '交易量(紅K)',
  if(`Change` <  0, TradeVolume, 0) as '交易量(綠K)'
FROM `taiwan_stock_price`
WHERE StockID = '{{股票代碼}}'
```
→ 一個欄位拆成漲(紅)/跌(綠)兩欄，各設顏色。

## 三、JOIN：合併多張表（面試常考）

把「融資融券」表 join「股價」表，一次 Query 拿兩種資料：
```sql
SELECT
  m.stock_id as "股票代碼", m.date as "日期",
  m.MarginPurchaseBuy as "融資買進",
  p.Close as "收盤價"
FROM taiwan_stock_margin_purchase_short_sale m
LEFT JOIN taiwan_stock_price p
  ON p.StockID = m.stock_id          -- 根據什麼欄位 join
  AND p.Date = m.date                -- 多欄 join 用 AND
WHERE m.stock_id = '0050'
```
JOIN 種類（左/右/內）：
- **LEFT JOIN**：以左表為主，右表沒對到就 NULL。
- **RIGHT JOIN**：以右表為主。
- **INNER JOIN**：只留兩邊都有對到的。
- `資料表.欄位` 表示某表的某欄；大小寫不影響關鍵字。

> 心法：**資料可先存成不同 Table**，之後用 join 組合即可——所以[第 23 章](23_worker_upload_mysql.md)分表存沒關係。

## 四、組成 Dashboard

建好多個 Query/圖 → 建立 **Dashboard** → Add Widget 把圖加進來 → Done Editing。使用者可切換股票代碼/日期，即時看圖。

> 為什麼兩張表（價格 vs 融資）畫同一張圖？**尺度不同，疊在一起才看得出相關性**。

## 常見錯誤

- **MySQL 沒資料就想視覺化**：要先有資料（跑完[爬蟲→上傳](23_worker_upload_mysql.md)）。
- **Host 寫 127.0.0.1**：docker 內要用服務名稱 `mysql`。
- **參數 `{{ }}` 沒設 Query Based/Date Range**：不會變成下拉/日期選單。
- **join 沒寫 ON 條件**：會變成笛卡兒積（資料爆炸）。

## 小練習

1. 用 Redash 連你的 MySQL，畫一檔股票的「收盤價」折線圖。
2. 加一個「股票代碼」下拉選單 + 日期區間。
3. 想一想：你的 ETF 專題可以畫「各 ETF 的 `adj_close` 長期走勢」「含息 vs 不含息」對照圖放進報告。

⬅ 上一章：[24 API：FastAPI](24_api_fastapi.md) ｜ ➡ 下一章：[26 Docker Swarm 介紹](26_docker_swarm_intro.md)
