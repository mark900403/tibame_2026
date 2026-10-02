# 16 · DML：新增 / 刪除 / 修改

> 對應課程：03 MySQL-DML
> DML = Data Manipulation Language（資料操作語言），用來**新增、刪除、修改** Table 內的資料。

## 重點摘要

三個指令：
- **`insert`**：新增資料列。
- **`delete`**：刪除資料列。
- **`update`**：修改資料。

執行完可能會異動資料，所以 `delete`/`update` **實務上一定要寫 `where` 條件**，否則會動到整張表。

## 一、insert：新增

### 基本語法
```sql
insert into 資料表名 [(欄位1, 欄位2, ...)]
values (值1, 值2, ...) [, (值1, 值2, ...)];
```
- **省略欄位名** → 代表「全部欄位都要給值」，且值要**依表格欄位順序**排列。
- 有寫欄位名 → 值依你列的欄位順序對應；沒列到的欄位用預設值/null。
- 值的型態要與欄位相容。

### 範例
```sql
-- 新增一筆（不寫欄位 = 全部欄位都要照順序給值）
insert into EMP
values (9999, 'William', 'Engineer', 7566, NOW(), 5500, 0, 20);

-- 新增多筆，並指定欄位名稱（沒列到的欄位如 COMM 會用預設）
insert into EMP (EMPNO, ENAME, JOB, MGR, HIREDATE, SAL, DEPTNO)
values
  (9999, 'William', 'Engineer', 7566, NOW(), 5500, 20),
  (8888, 'Reds',    'Engineer', 7566, NOW(), 6500, 20);
```
- `NOW()`：MySQL 內建函式，取現在的日期時間。

### 變化型：insert ... select（從查詢結果新增）
把另一段查詢的結果直接塞進表——欄位數要一致、型態相容：
```sql
-- 複製 EMPNO=9999 的資料，改成 7777 再新增
insert into EMP (EMPNO, ENAME, JOB, HIREDATE, SAL, COMM, DEPTNO)
select 7777, ENAME, JOB, HIREDATE, SAL, COMM, DEPTNO
from EMP
where EMPNO = 9999;
```

## 二、delete：刪除

### 基本語法
```sql
delete from 資料表名 where 條件;
```
- **不寫 `where` → 刪光整張表所有列！** 實務上一定要有條件。

### 範例
```sql
-- 刪除 EMPNO 為 7777 的那一列
delete from EMP where EMPNO = 7777;
```

### 變化型：用子查詢當條件
```sql
-- 刪除在 'SALES' 部門工作的所有員工
delete from EMP
where DEPTNO = (select DEPTNO from DEPT where DNAME = 'SALES');
```

## 三、update：修改

### 基本語法
```sql
update 資料表名
set 欄位1 = 值1, ..., 欄位N = 值N
where 條件;
```
- **不寫 `where` → 修改所有列！** 一定要有條件。
- `set` 裡可以用「現有欄位」運算，例如加薪。

### 範例
```sql
-- 修改 EMPNO=9999：改名 + 薪水加 500
update EMP
set ENAME = 'William Lee',
    SAL   = SAL + 500
where EMPNO = 9999;
```

### 變化型：子查詢用在 set 或 where
```sql
-- (子查詢在 set) 把部門 10 的員工，調到 'ACCOUNTING' 部門
update EMP
set DEPTNO = (select DEPTNO from DEPT where DNAME = 'ACCOUNTING')
where DEPTNO = 10;

-- (子查詢在 where) 替 'SALES' 部門所有員工加薪 500
update EMP
set SAL = SAL + 500
where DEPTNO = (select DEPTNO from DEPT where DNAME = 'SALES');
```

## 常見錯誤

- **`delete` / `update` 忘了 `where`** → 整張表遭殃。養成先寫 `where` 的習慣，或先用相同條件 `select` 確認會動到哪些列。
- **`insert` 值的順序/數量對不上欄位** → 報錯或存錯欄。不確定就**明確列出欄位名**。
- **字串沒加單引號**：`'William'` 要引號；數字不用。
- **型態不相容**：例如把文字塞進 `int` 欄位。
- **忘了交易保護**：大量異動前可搭配交易控制（[17 章 TCL](17_tcl.md)），錯了能 `rollback`。

## 小練習（改自課程 Exercise07）

1. 新增一筆部門：`50, 'Software', 'Taipei'` 到 `DEPT`。
2. 新增兩位員工（欄位 EMPNO, ENAME, JOB, MGR, HIREDATE, SAL, DEPTNO）：
   `9999,'William','PG',null,NOW(),2500,50` 與 `8888,'Lee','PM',null,NOW(),3500,50`。
3. 把 8888 的主管改成 7839；再刪除 8888；最後把 9999 的主管改 7839、薪水改 4000。

⬅ 上一章：[15 SQL 與 MySQL 總覽](15_sql_mysql_intro.md) ｜ ➡ 下一章：[17 TCL：交易控制](17_tcl.md)
