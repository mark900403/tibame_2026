# 19 · View 與 Index

> 對應課程：07 MySQL-其他物件
> 兩個常用的資料庫物件：**View（檢視表）** 和 **Index（索引）**。

## Part A · View（檢視表）

### 重點摘要
**View** 是「由一段 `select` 定義出來的虛擬表」。它本身**不存資料**，每次用到就重跑那段 select，呈現查詢結果。命名習慣加前綴 **`V_`** 以區別真實 Table。

### 核心觀念
- **虛擬 vs 實體**：View 是虛擬結構（不存資料）；Table 才是實體結構（真的存資料）。
- **基底資料表(Based Table)**：定義 View 用到的資料來源（通常是 Table，也可以是另一個 View）。
- **常見用途**：
  - 簡化複雜查詢：程式端只對 View 操作；查詢需求變了只改 View，不動程式。
  - 隱藏/限制資料：只讓工程師看到部分欄位；設計成唯讀避免亂改。
- **效能**：每次用到都重跑 select，複雜 View 要注意效能。

### 新建 View
```sql
create [or replace] view 檢視表名 [(欄位名1, ...)]
as
子查詢
[with [cascaded | local] check option];
```
```sql
-- 只含部門 30 員工
create view V_EMP30 as
select * from EMP where DEPTNO = 30;

-- 指定呈現欄位名（數量要跟 select 相同）
create view V_EMP30(NO, NAME, TITLE, MGR_NO) as
select EMPNO, ENAME, JOB, MGR from EMP where DEPTNO = 30;
```

### with check option（透過 View 改資料時的守門員）
對 View 做 DML（insert/update）時，**檢查改完的資料是否仍符合 View 的 `where`**，不符合就報錯 `CHECK OPTION failed`。
- `cascaded`（預設）：連基底 View 的條件一起檢查；`local`：只檢查當前 View。
```sql
create view V_EMP30 as
select * from EMP where DEPTNO = 30
with check option;

-- 這筆 DEPTNO=10，不符合 V_EMP30 的 where(DEPTNO=30) → 失敗
insert into V_EMP30 (EMPNO, ENAME, DEPTNO) values (9999, 'William', 10);
```

### 修改 / 移除 View
```sql
alter view V_EMP30 as
select * from EMP where DEPTNO = 30 and MGR is not null;

drop view if exists V_EMP30;
```
> View 可能是其他 View 的基底，修改/移除後可能造成別的 View 出錯。

### 可異動資料的 View（限制）
對 View 做 DML 會改到底層 Table，但**有條件**才安全。可安全異動要滿足：**沒有計算欄位/函式欄位**、**基底表只有一個**。
```sql
-- 用了兩張表 join，仍可 update，但結果可能出乎預期
create view V_UPDATABLE as
select e.EMPNO, e.ENAME, d.DEPTNO, d.DNAME
from EMP e join DEPT d on e.DEPTNO = d.DEPTNO;

update V_UPDATABLE set DNAME = '會計部' where EMPNO = 7782;
-- ⚠ 結果：同部門好幾個員工的 DNAME 都變了！
```
> 「計算欄位」= 靠計算得到的欄位，如「年薪 = 月薪*12」。

## Part B · Index（索引）

### 重點摘要
**Index** 就像書的**目錄**：查資料時能快速定位，不用整本翻。針對某表的一或多個欄位建立，以**平衡樹(B-Tree)** 儲存。

### 核心觀念（空間換時間）
- **沒 Index**：查詢要掃整張表（Full Table Scan）。
- **有 Index**：像查目錄，幾次比對就找到。
- 代價：Index **佔大量硬碟**，且**資料異動(insert/delete/update)時要重建**，所以**不是建越多越好**。
- 對 `select` 是加速；對 DML 反而是負擔。

### Index 種類
| 種類 | 特性 | 怎麼來 |
|------|------|--------|
| 主要索引 Primary | 值不可重複、不可 null，一表一個 | 建 **Primary Key** 時自動產生（不能直接建） |
| 唯一索引 Unique | 值不可重複 | 建 **Unique Key** 時自動產生（MySQL 中兩者等效） |
| 一般索引 | 純加速，無其他特性 | 可直接建；建 **Foreign Key** 時也會自動產生 |
| 複合索引 | 由 2 個以上欄位組成 | 上述皆可設計成複合 |

### 新建 Index（三種寫法）
命名習慣：`IDX_資料表名_欄位名`
```sql
-- 1) 獨立建立
create index IDX_EMP_ENAME on EMP(ENAME);
create unique index IDX_DEPT_DNAME on DEPT(DNAME);

-- 2) 建表時一起建
create table DEPT (
  DEPTNO int not null primary key,
  DNAME  varchar(15),
  LOC    varchar(15),
  unique index IDX_DEPT_DNAME(DNAME)
);

-- 3) 用 alter table 加
alter table DEPT add index IDX_DEPT_LOC(LOC);
-- 複合索引
alter table EMP add index IDX_EMP_DEPTNO_ENAME(DEPTNO, ENAME);
```

### 移除 Index
```sql
drop index IDX_DEPT_DNAME on DEPT;
-- 或
alter table DEPT drop index IDX_DEPT_LOC;
```

### 什麼時候該建 Index？（適用時機）
建 Index 划算的情況：
- **資料量大**（如 60 萬筆以上）。
- 該表**常查(select)、少改(insert/delete/update)**。
- 欄位**值域分布廣、重複少、null 少**（像「性別」只有兩種值就不適合）。
- 欄位常出現在 `where`、`group by`、`order by`、`join on`，或常用 `MAX()`/`MIN()`。

## 常見錯誤

- **View 當成有存資料** → 它是虛擬的，每次重算；複雜 View 會慢。
- **對多表 join 的 View 做 update** → 可能一次改到多列，結果非預期。
- **Index 亂建一堆** → 拖慢寫入、佔空間。挑對欄位、看資料量再建。
- **想直接建主要索引** → 不行，要透過建 Primary Key 間接產生。

## 小練習（改自課程 Exercise11/12）

1. 建 View `V_DEPT_ECOUNT` 列出「部門編號、部門人數」（提示：`group by DEPTNO`）。
2. 替 `DEPT.DNAME` 建唯一索引，並取合適名稱。
3. 替 `EMP(DEPTNO, ENAME)` 建複合索引 `IDX_EMP_DEPTNO_ENAME`，想想查詢時它對哪種 `where` 有幫助。

⬅ 上一章：[18 DCL](18_dcl.md) ｜ ➡ 下一章：[20 PyMySQL](20_pymysql.md)
