# 22 · 專案結構與用 Docker 部署 MySQL（Transform）

> 對應課程：09/19（MySQL Transform 1）

## 重點摘要

這章兩件事：(1) 一個 side project 的 **GitHub 資料夾結構**該怎麼規劃；(2) 用 **Docker 一鍵部署 MySQL + phpMyAdmin**，把爬到的資料存進資料庫（ETL 的 **Transform/儲存**）。

## 一、專案資料夾結構

參考講師專案 [TibameSam/crawler](https://github.com/TibameSam/crawler)、[FinMind](https://github.com/FinMind/FinMind)：

```
crawler/                 ← 專案根目錄
├─ crawler/              ← 主程式放一個資料夾內（這樣才能變成 module）
│   ├─ producer.py       發送任務
│   ├─ worker.py         工人
│   ├─ tasks.py          定義任務
│   └─ scheduler.py      排程
├─ Dockerfile            ← 與 crawler 同層
├─ pyproject.toml        ← uv 專案設定；讓 crawler 變成可 import 的 module
├─ uv.lock
├─ docker-compose.yml
├─ genenv.py             產生 .env
├─ rabbitmq.yml / mysql.yml
├─ figure/               圖片
├─ data/                 資料（自行新增）
└─ README.md             指令筆記
```

**為什麼主程式要放在子資料夾？**
- `pyproject.toml` 把 `crawler` 變成一個 **module**，之後才能 `import crawler...`。
- 放錯階層就無法變成 module。
- 爬下來的 data 可先存 GitHub，或另開 repo 存。

> 重點心法：準備一份自己常用的 side project 結構，新 repo 幾乎照抄（講師開發 10+ repo 都是 copy & paste）。

## 二、為什麼要用資料庫（而不是一直存 CSV）？

- 台股一年 ~200 交易日 × 多種資料（股價、三大法人、融資融券）→ 10 年就是**上千個 CSV**，無法管理。
- 業界資料量：千萬～上億筆、數 GB。
- **worker 在 container 內跑，輸出的 CSV 關閉後就消失**；worker 又分散在很多台 VM，不可能手動去每台撈 CSV。
- 所以把爬到的資料**統一上傳 MySQL**。

## 三、用 Docker 一鍵部署 MySQL + phpMyAdmin

```bash
docker compose -f mysql.yml up -d      # 一鍵部署 MySQL + phpMyAdmin
docker volume ls                       # 查看 MySQL 的資料卷(volume)
```

`mysql.yml` 兩個服務：
1. **mysql**：`image`、`command`（設定密碼加密方式）、`port`、`environment`（root 密碼等）、`volumes`（資料持久化）、`network`。
2. **phpmyadmin**：`image`、`port`、`depends_on`（等 mysql）、`volumes`。

用瀏覽器管理：`http://127.0.0.1:8080/`（帳密 root / 自訂密碼）。
> ⚠ 要先**關閉 Windows 本機的 MySQL**（工作管理員找到 mysql 關掉），否則 port 3306 衝突。

### phpMyAdmin 是什麼？
- MySQL 的**網頁圖形化管理介面**。
- 好處：雲端部署後，電腦不用裝任何工具，開網頁就能管理、監控資料庫（新增 database/table、設欄位型態、設主鍵）。

### 用 phpMyAdmin 建表 + 設主鍵
- 新增 database → 新增 table → 設定欄位名稱/型態 → 儲存。
- **設主鍵**：勾選 `date` & `stock_id` → 設為主鍵（出現鑰匙圖示）。

## 四、主鍵（Primary Key）的三大特性

| 特性 | 說明 / 對爬蟲的意義 |
|------|------|
| **唯一性 Unique** | 避免資料重複——爬蟲重複上傳同一天同一檔，不會變兩筆 |
| **非空 NOT NULL** | 確保資料完整，避免爬蟲異常 |
| **自動建 Index** | 查大量資料時，有設主鍵 vs 沒設，效能可差到 **100 倍** |

> 這呼應 [16 章 DML](16_dml.md)、[19 章 Index](19_view_index.md)：主鍵會自動建主要索引。

## 五、常見資料庫種類

| 類型 | 代表 | 適用情境 |
|------|------|----------|
| **RDB 關聯式** | MySQL、PostgreSQL | 結構化資料：商品、用戶、訂單、股價 |
| **NoSQL 非關聯式** | Redis、MongoDB | Redis 存記憶體（快 20 倍+），做快取：登入資訊（1 萬人登入不可能查 MySQL 1 萬次） |
| **TSDB 時間序列** | InfluxDB、TimescaleDB | 隨時間嚴格遞增、過去不變：log、監控、股價 |

> 實務上會**混用** RDB / NoSQL / TSDB，依情境切換。

## 常見錯誤

- **port 3306 衝突**：先關掉本機 Windows MySQL。
- **沒設 volume**：容器關閉資料就不見（要 `volumes` 持久化）。
- **主程式沒放子資料夾**：`pyproject.toml` 無法把它變成 module，之後 import 失敗。
- **一直存 CSV**：小練習可以，但多來源/多機/大量就該進資料庫。

## 小練習

1. 用 `docker compose -f mysql.yml up -d` 起一個 MySQL，用 phpMyAdmin 建一張 `(date, stock_id, close)` 的表並設主鍵。
2. 說出「為什麼 worker 的 CSV 不可靠、要改存資料庫」。
3. 想一想：你的 ETF 專題各種資料（股價/除權息/分割）適合 RDB、NoSQL 還是 TSDB？

⬅ 上一章：[21 環境管理與排程](21_env_config_scheduler.md) ｜ ➡ 下一章：[23 Worker 上傳 MySQL 與自動去重](23_worker_upload_mysql.md)
