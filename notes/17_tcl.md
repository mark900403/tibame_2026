# 17 · TCL：交易控制

> 對應課程：04 MySQL-TCL
> TCL = Transaction Control Language（交易控制語言）。

## 重點摘要

**交易(Transaction)** = 由多個 SQL 敘述組成的「一整組動作」，商業邏輯上常要求：**要嘛全部成功，要嘛全部失敗（不留半套）**。成功就**送交 `commit`**，失敗就**還原 `rollback`**。

經典例子：轉帳——A 扣 300、B 加 300，這兩步必須同生共死；只做一半就出大事。

## 核心觀念

- MySQL 只有 **InnoDB 引擎**支援交易控制。
- 交易開始後，DML 會產生**列鎖定(Row Locking)**（避免別人同時改同一列造成混亂）。
- 兩種開啟交易的方式：**關閉 autocommit** 或 **start transaction**。

## 一、開始交易

### 方式 A：`set autocommit`（全域開關，影響當前連線之後所有敘述）
```sql
set autocommit = 0;      -- 啟用交易控制（改成手動送交）
select @@autocommit;     -- 查目前設定
set autocommit = 1;      -- 停用（回到自動送交狀態）
```
> 記法（有點反直覺）：`autocommit = 0` = **關掉自動送交** = **啟用**手動交易控制；`= 1` = 自動送交。
> 只影響**當前連線**，其他連線不受影響；一旦設定會一直保持，要自己設回來。

### 方式 B：`start transaction`（只影響這一段單一交易）
```sql
start transaction;
-- ... 一組 DML ...
commit;   -- 或 rollback
```
- 從 `start transaction` 到 `commit`/`rollback` 稱為**一個單一交易**。
- 執行到 `commit`/`rollback` 就結束，回到自動送交狀態（比 A 方便，不用記得設回來）。

## 二、結束交易

```sql
commit;     -- 送交：把這組動作正式寫入資料庫
rollback;   -- 還原：把未送交的動作全部取消
```
> `commit`/`rollback` 要搭配 `set autocommit = 0` 或 `start transaction` 才有意義。

### savepoint：交易中的「存檔點」
```sql
savepoint 儲存點名;          -- 設一個存檔點（名稱自訂、不可重複、區分大小寫）
rollback to 儲存點名;        -- 只還原到這個存檔點（後面的動作取消，前面的保留）
```
- `rollback` 不加 `to` → 還原**所有**未送交動作。
- `rollback to p2` → 只還原 p2 之後的動作。

## 完整範例

### 例 1：轉帳（兩步同生共死）
```sql
-- 方式一：autocommit
set autocommit = 0;
update EMP set COMM = COMM - 300 where EMPNO = 7499;
update EMP set COMM = COMM + 300 where EMPNO = 7521;
commit;              -- 兩步都 OK 才送交
set autocommit = 1;  -- 記得設回自動送交

-- 方式二：start transaction（推薦）
start transaction;
update EMP set COMM = COMM - 300 where EMPNO = 7499;
update EMP set COMM = COMM + 300 where EMPNO = 7521;
commit;
```
> 中途若發現不對，把 `commit` 換成 `rollback`，兩步都不算數。

### 例 2：savepoint 局部還原
```sql
start transaction;
delete from EMP where DEPTNO = 10;
savepoint p1;
delete from EMP where DEPTNO = 20;
savepoint p2;
delete from EMP where DEPTNO = 30;
rollback to p2;   -- 還原「刪部門30」；刪部門10、20仍保留
                  -- 若改成 rollback to p1，則只有刪部門10保留
```

## 常見錯誤

- **以為 `autocommit=1` 是開啟交易** → 相反！`=0` 才是啟用手動交易控制。
- **忘了 `commit`** → 你的改動在別的連線看不到；連線結束可能整批消失。
- **用 autocommit 方式後忘了設回 `=1`** → 之後每次都要手動 commit，容易忘記造成困惑。改用 `start transaction` 較單純。
- **在非 InnoDB 表用交易** → 不支援，交易控制無效。
- **`rollback to` 一個沒設過的 savepoint** → 報錯。

## 小練習（改自課程 Exercise08）

1. 啟用交易控制，刪除「除了老闆以外」的所有員工 → 查詢確認 → `rollback` 還原。
2. 用 `start transaction`，把非老闆員工「獎金+1000、薪水+15%」→ 查詢確認 → `commit`。
3. 想一想：爬蟲一次要寫入多張關聯表時，為什麼用交易能避免「寫一半」的髒資料？（連到 [20 章 PyMySQL](20_pymysql.md) 的 commit/rollback）

⬅ 上一章：[16 DML](16_dml.md) ｜ ➡ 下一章：[18 DCL：權限控制](18_dcl.md)
