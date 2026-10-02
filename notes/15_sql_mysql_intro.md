# 15 · SQL 與 MySQL 總覽

> 對應課程：MySQL 系列（講師：李偉銘）——這是資料庫段落的入口
> 需要工具：MySQL Server + 一個客戶端（Workbench，或用 [20 章 PyMySQL](20_pymysql.md) 用 Python 連）

## 重點摘要

前面我們把資料爬下來、用 pandas 存成 CSV。但要長期、可查詢、可多人共用地保存資料，就需要**資料庫**。這門課用 **MySQL**（最流行的關聯式資料庫之一），並用 **SQL** 語言來操作它。

> 對照課程大架構（[第 09 章](09_architecture_and_dev_env.md)）：`Crawler → MySQL → API / Dashboard`。這一段就是把「爬到的資料」正式存進 MySQL。

## 核心觀念

### 1. 關聯式資料庫 = 一堆「表格」
- **Table（資料表）**：像 Excel 的一張表，有欄(Column)有列(Row)。
- **Column 欄位**：一個屬性（如 姓名、薪水）。
- **Row 資料列**：一筆紀錄（一個員工）。
- 多張表之間用「共同欄位」關聯（例如員工表的部門編號 對應 部門表）。

### 2. 課程的範例資料庫：EMP / DEPT
課程所有範例都用兩張經典表：

`DEPT`（部門）
| DEPTNO | DNAME | LOC |
|--------|-------|-----|
| 10 | ACCOUNTING | ... |
| 30 | SALES | ... |

`EMP`（員工）
| EMPNO | ENAME | JOB | MGR | HIREDATE | SAL | COMM | DEPTNO |
|-------|-------|-----|-----|----------|-----|------|--------|
| 7499 | ... | ... | 7698 | ... | 1600 | 300 | 30 |

- `EMP.DEPTNO` 對應 `DEPT.DEPTNO`（員工屬於哪個部門）。
- `EMP.MGR` 是主管的 `EMPNO`（自己參照自己）。

### 3. SQL 的五大分類（很重要的地圖）
SQL 依「用途」分成五類，這門課逐一介紹：

| 縮寫 | 全名 | 白話 | 代表指令 | 本教材 |
|------|------|------|----------|--------|
| **DQL** | Data Query Language | **查詢**資料 | `select` | 背景（見下） |
| **DML** | Data Manipulation Language | **增刪改**資料 | `insert` / `delete` / `update` | [16 章](16_dml.md) |
| **DDL** | Data Definition Language | **定義**結構 | `create/alter/drop table` | 背景（見下） |
| **TCL** | Transaction Control Language | **交易**控制 | `commit` / `rollback` | [17 章](17_tcl.md) |
| **DCL** | Data Control Language | **權限**控制 | `grant` / `revoke` | [18 章](18_dcl.md) |

此外還有 **View（檢視表）** 與 **Index（索引）** 等物件 → [19 章](19_view_index.md)；用 **Python 操作 MySQL** → [20 章 PyMySQL](20_pymysql.md)。

## 背景補充：DQL(select) 與 DDL(create table) 速覽

> 這兩份投影片本次未提供，但後面章節的範例會用到。這裡給**最精簡**的背景，看得懂範例即可；正式內容以課程的 DQL/DDL 投影片為準。

### DQL：查詢 `select`（最常用）
```sql
select 欄位1, 欄位2      -- 要哪些欄（* 代表全部）
from   資料表           -- 從哪張表
where  條件             -- 篩選哪些列
order by 欄位            -- 排序
limit  10;              -- 只取前幾筆
```
例：查部門 30 的員工姓名與薪水
```sql
select ENAME, SAL from EMP where DEPTNO = 30;
```

**子查詢（subquery）**：把一個查詢的結果，當作另一個敘述的條件（DML 章會用到）：
```sql
-- 找出 DNAME 是 'SALES' 的部門編號，拿去當條件
where DEPTNO = (select DEPTNO from DEPT where DNAME = 'SALES')
```

**join**：把兩張表用共同欄位接起來一起查：
```sql
select e.ENAME, d.DNAME
from EMP e join DEPT d on e.DEPTNO = d.DEPTNO;
```

### DDL：建立表格 `create table`
```sql
create table DEPT (
  DEPTNO int not null primary key,   -- 主鍵：唯一、不可 null
  DNAME  varchar(15),                -- 可變長字串，最長 15
  LOC    varchar(15)
);
```
- 常見型態：`int`（整數）、`varchar(n)`（字串）、`date`/`datetime`（日期時間）。
- **primary key 主鍵**：一張表唯一識別一列的欄位（如 EMPNO）。
- **foreign key 外來鍵**：指向另一張表主鍵的欄位（如 EMP.DEPTNO → DEPT.DEPTNO）。

## 小提醒（SQL 寫作習慣）

- SQL **關鍵字大小寫不敏感**（`SELECT` = `select`），但字串值（`'SALES'`）大小寫敏感。
- 字串用**單引號** `'...'`。
- 每條敘述用 **`;`** 結尾。
- 註解：`# ...`、`-- ...`（單行）、`/* ... */`（多行）。

## 小練習

1. 說出 EMP 表裡「一列」代表什麼、「一欄」代表什麼。
2. 寫一句 `select`，查出薪水大於 2000 的所有員工姓名。
3. 對照 SQL 五大分類，說出「新增一筆員工」「調薪」「刪表」各屬哪一類。

⬅ 回 [課程總覽](../README.md) ｜ ➡ 下一章：[16 DML：新增/刪除/修改](16_dml.md)
