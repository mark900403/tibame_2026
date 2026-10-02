# 18 · DCL：權限控制

> 對應課程：06 MySQL-DCL
> DCL = Data Control Language（資料控制語言），用來控制**使用者(User)對資料庫各物件的權限**。

## 重點摘要

- **`grant`**：授出權限。
- **`revoke`**：撤回權限。
- 核心觀念：不是每個使用者都該有全部權限。該給的給、該收的收，保護資料安全。

## 核心觀念：使用者帳號 `使用者名@網域名`

要連線到資料庫伺服器，就需要**使用者帳號**。格式是 **`使用者名@網域名`**：
- **使用者名(Username)**：使用者名稱。
- **網域名(Host)**：允許從哪裡連線，可用網域/IP，或用 **`%`** 表示不限。

```text
root@localhost          -- 使用者 root，只能在資料庫本機使用
william@192.168.43.5    -- william 只能從這個 IP 連線
lee@%                   -- lee 可以從任何地方連線
```
> 安裝 MySQL 時預設就有 `root@localhost`。可用 Workbench 圖形介面新建使用者。

## 一、grant：授出權限

### 語法
```sql
grant 權限1, ..., 權限N
on   [資料庫名.]物件名
to   使用者帳號1, ..., 使用者帳號N
[with grant option];
```
- **權限**：要授出的權限（如 `select`、`insert`、`update`… 或 `all` 全部）。
- **`on 資料庫.物件`**：作用對象，可用 **`*.*`** 代表「所有資料庫的所有物件」。
- **`with grant option`**：讓對方也能「把權限再轉授」給別人。

### 範例
```sql
-- 授出「所有物件的所有權限」給 william，且他能再轉授給別人
grant all
on *.*
to 'william'@'192.168.43.5'
with grant option;
```

實務上更常見的是**只給特定資料庫、特定權限**（最小權限原則）：
```sql
-- 只給 EXAMPLE 資料庫底下所有物件的「查詢與新增」權限
grant select, insert
on EXAMPLE.*
to 'william'@'%';
```

## 二、revoke：撤回權限

### 語法
```sql
revoke 權限1, ..., 權限N
on   [資料庫名.]物件名
from 使用者帳號1, ..., 使用者帳號N;
```

### 範例
```sql
-- 撤回 william 對所有物件的所有權限
revoke all
on *.*
from 'william'@'192.168.43.5';

-- 只撤回「轉授權限的權限」（保留其它權限）
revoke grant option
on *.*
from 'william'@'192.168.43.5';
```

## 常見權限一覽（挑常用）

| 權限 | 作用 |
|------|------|
| `select` | 查詢 |
| `insert` / `update` / `delete` | 新增 / 修改 / 刪除資料 |
| `create` / `drop` | 建立 / 移除資料庫或表 |
| `all` | 全部權限 |
| `grant option` | 可把權限再轉授他人 |

> 完整清單見官方 Manual 的 GRANT Statement。

## 用 Workbench 確認權限
Workbench → 左側 **Administration → Users and Privileges** → 選帳號 → 頁籤 **Schema Privileges**，即可查看/調整授出的權限。

## 常見錯誤 / 安全建議

- **一律給 `all on *.*`** → 權限過大很危險。遵循**最小權限原則**：只給該給的資料庫與動作。
- **帳號 Host 開 `%` 又給高權限** → 等於全世界都能用高權限連，風險高。限制來源 IP。
- **忘記 `with grant option` 的連鎖影響** → 對方能把權限散出去；撤回時記得也處理轉授。
- **改了權限沒生效** → 某些情況需重新連線；用 Workbench 確認。

## 小練習（改自課程 Exercise10）

1. 用 Workbench 建立帳號：Username `william`、Host `%`、密碼 `P@ssw0rd`。
2. 授出對資料庫 `EXAMPLE` 底下所有物件的所有權限給 `william`。
3. 再從 `william` 撤回上述權限，並用 Workbench 的 Schema Privileges 確認。

⬅ 上一章：[17 TCL](17_tcl.md) ｜ ➡ 下一章：[19 View 與 Index](19_view_index.md)
