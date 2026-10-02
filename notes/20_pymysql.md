# 20 · PyMySQL：用 Python 操作 MySQL

> 對應課程：09 MySQL-PyMySQL
> 需要套件：`pymysql`（`pip install pymysql`，或 `uv add pymysql`）

## 重點摘要

**PyMySQL** 是純 Python 寫的 MySQL 客戶端函式庫，遵循 Python 資料庫標準 **DB API (PEP 249)**。有了它，就能**用 Python 連 MySQL、執行 SQL、取得結果**——等於用程式代替你手動在資料庫工具裡打 SQL。

> 這一章把前面兩條線接起來：[爬蟲](05_web_crawling_api_json.md)抓到的資料 → 用 PyMySQL 寫進 [MySQL](15_sql_mysql_intro.md)。

## 一、安裝
```bash
pip install pymysql
# 或（uv 專案，見第 13 章）
uv add pymysql
```

## 二、取得連線（Connection）

所有操作都從「連到資料庫」開始：
```python
from typing import Any
import pymysql
from pymysql.connections import Connection

def get_connection() -> Connection:
    return pymysql.connect(
        host="localhost",        # 資料庫伺服器位置
        user="root",             # 使用者
        password="password",     # 密碼
        database="EXAMPLE",      # 要用哪個資料庫
        charset="utf8mb4",       # 編碼（utf8mb4 才完整支援中文/emoji）
        cursorclass=pymysql.cursors.DictCursor,  # 讓查詢結果是 dict（欄名:值）
    )
```
- **cursor（游標）**：實際下 SQL、拿結果的物件。
- `DictCursor`：查詢結果每列變成 `dict`（如 `{"EMPNO": 7499, ...}`），比預設的 tuple 好讀。

## 三、核心流程與「參數化查詢」

固定套路：**取得連線 → 開 cursor → `execute(sql, 參數)` → 查詢用 `fetch` / 異動用 `commit`**。

⚠ **千萬不要用字串拼接把值塞進 SQL**（會有 SQL Injection 風險）。用 **佔位符 + 參數** 讓 PyMySQL 幫你安全代入：
- `%s`：位置參數（依序對應）。
- `%(名字)s`：具名參數（對應 dict 的 key）。

### 新增 insert（具名參數 + 交易）
```python
def insert(emp: dict[str, Any]) -> int:
    sql = """
        insert into EMP
        values (%(empno)s, %(ename)s, %(job)s, %(mgr)s,
                %(hiredate)s, %(sal)s, %(comm)s, %(deptno)s)
    """
    try:
        with get_connection() as conn:            # with：用完自動關閉連線
            with conn.cursor() as cursor:
                num = cursor.execute(sql, emp)    # emp 是 dict，對應 %(key)s
                conn.commit()                     # 異動一定要 commit 才會真的寫入
                return num                        # 回傳受影響的列數
    except Exception:
        conn.rollback()                           # 出錯就還原（對應 TCL）
        raise
```

### 刪除 delete（位置參數）
```python
def delete_by_empno(empno: int) -> int:
    sql = "delete from EMP where EMPNO = %s"     # %s 佔位符
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                num = cursor.execute(sql, empno)
                conn.commit()
                return num
    except Exception:
        conn.rollback()
        raise
```

### 修改 update
```python
def update_by_empno(emp: dict[str, Any]) -> int:
    sql = """
        update EMP
        set ENAME=%(ename)s, JOB=%(job)s, MGR=%(mgr)s,
            SAL=%(sal)s, COMM=%(comm)s, DEPTNO=%(deptno)s
        where EMPNO=%(empno)s
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                num = cursor.execute(sql, emp)
                conn.commit()
                return num
    except Exception:
        conn.rollback()
        raise
```

### 查詢 select（`fetchone` / `fetchall`）
查詢**不需要** commit：
```python
def select_by_empno(empno: int) -> dict[str, Any]:
    sql = "select * from EMP where EMPNO = %s"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, empno)
            return cursor.fetchone()     # 取「一筆」（dict）

def select_all() -> list[dict[str, Any]]:
    sql = "select * from EMP"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()     # 取「全部」（list of dict）
```

## 重點整理

| 動作 | 要 commit? | 取結果 |
|------|:---------:|--------|
| insert / update / delete | ✅ 要 | `execute` 回傳受影響列數 |
| select | ❌ 不用 | `fetchone()` 一筆 / `fetchall()` 全部 |

- **異動要 `commit`**（呼應 [17 章 TCL](17_tcl.md)）；出錯 `rollback`。
- **值一律用參數化**（`%s` / `%(key)s`），不要字串拼接。
- **`with` 管理連線/游標**：用完自動關閉，避免連線洩漏。

## 串起專題：把爬蟲資料寫進 MySQL

```python
# 假設 crawler 回傳 list of dict（見第 05/07 章）
rows = crawl()                    # [{"empno":..., "ename":..., ...}, ...]
for row in rows:
    insert(row)                   # 一筆筆寫入（或用 cursor.executemany 批次）
```
> 進階：`cursor.executemany(sql, rows)` 可一次寫多筆，效能更好；大量寫入時搭配交易一次 `commit`。

## 常見錯誤

- **忘了 `commit`** → insert/update/delete「看起來成功」卻沒真的寫入（連線關掉就沒了）。
- **用 f-string 拼 SQL** → SQL Injection 風險 + 中文/引號易出錯。務必用參數化。
- **`fetchone` 當成 `fetchall`** → 只拿到一筆還以為全部。
- **charset 沒設 utf8mb4** → 中文變亂碼。
- **連線沒關** → 用 `with`（context manager）自動關。
- **例外沒處理** → 異動失敗沒 `rollback`，可能留下半套資料。

## 小練習（改自課程 Exercise13）

1. 對一張 `MEMBER` 表，寫 `insert(member)`、`delete_by_id(id)`、`select_all()`。
2. 寫 `update_by_username(member)`，但**只允許修改** `PASSWORD`、`NICKNAME` 兩欄。
3. 把[第 05 章](05_web_crawling_api_json.md)爬到的資料，改成用 `insert()` 寫進 MySQL（而不是存 CSV）。

⬅ 上一章：[19 View 與 Index](19_view_index.md) ｜ [名詞小字典](glossary.md) ｜ [專題步驟指南](../PROJECT_GUIDE.md)
