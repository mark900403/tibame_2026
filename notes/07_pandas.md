# 07 · pandas 資料處理

> 對應課程：08/22、08/28
> 需要套件：`pandas`（`pip install pandas`）、`glob`/`os`（內建）

## 重點摘要

**pandas** 是 Python 最重要的「表格處理」工具。核心型態是 **DataFrame**（就是一張會算術的表格）。課程強調 pandas 的**兩大操作**：
1. **過濾（filter）**：挑出想要的**列(row)**。
2. **轉換（transform）**：改變/新增某些**欄(column)**。

## 核心觀念

### 1. DataFrame 從哪來？
最常見：一堆 dict 組成的 list → 表格。
```python
import pandas as pd
table = [
    {"name": "A店", "rating": "4.5", "price": "1000"},
    {"name": "B店", "rating": "4.2", "price": "800"},
]
df = pd.DataFrame(table)   # 每個 dict 一列，key 變欄名
```

### 2. 讀寫檔案
```python
df.to_csv("out.csv", encoding="utf-8", index=False)  # 寫出
df = pd.read_csv("out.csv", encoding="utf-8")         # 讀入
```

### 3. 合併多個表格：`pd.concat`
爬很多頁時，每頁做成一個 df，最後合成一張大表：
```python
import glob, os
total = []
for fp in glob.glob("baha/*/*.csv"):     # glob：用萬用字元 * 找出符合的所有檔案路徑
    d = pd.read_csv(fp, encoding="utf-8")
    d["sn"] = os.path.basename(fp).replace(".csv", "")  # 新增一欄記來源
    total.append(d)
total_df = pd.concat(total)              # 上下疊起來變一大張
```
- `glob.glob("baha/*/*.csv")`：找出 `baha/任意資料夾/任意檔.csv`。
- `d["sn"] = ...`：**新增一欄**，整欄都填同一個值。

## 兩大操作

### A. 過濾（filter）＝ 用「一排 True/False」挑列
概念：準備一個和「列數一樣多」的布林清單，`True` 的留下、`False` 的丟掉。
```python
fil = [True, False, True]
df.head(3)[fil]            # 3 列中，留下第 0、2 列
```
實務上，布林清單通常由「條件」自動產生：
```python
fil = total_df["userid"] == "k9219059"   # 對整欄比較，得到一整排 True/False
total_df[fil]                            # 留下 userid 等於該值的所有列
```
常用輔助：
```python
total_df["userid"].unique()         # 這欄有哪些「不重複」的值
total_df["userid"].value_counts()   # 每個值各出現幾次
```

#### 應用：依 userid 把資料分檔
```python
for n in total_df["userid"].unique():
    fil = total_df["userid"] == n
    total_df[fil].to_csv(f"analyse/{n}.csv", encoding="utf-8", index=False)
```

### B. 轉換（transform）＝ 用 `apply` 對整欄套一個函式
`Series.apply(函式)`：把某一欄的每個值，都丟進函式處理，得到新的一欄。
```python
def func(n):
    return n * 2
total_df["rating"].astype(float).apply(func)   # 先轉成 float，再每個 *2
```
- `.astype(float)`：把整欄型態轉成小數（爬下來常是字串 `"4.5"`，要先轉才能算數）。
- `.apply(func)`：整欄逐一套用 `func`。

#### 進階：一次拆成多欄（回傳 `pd.Series`）
把 `"地區 / 類型"` 這種欄位，拆成兩欄 `area`、`genre`：
```python
def func(s):
    parts = s.split(" / ")
    ans = {"area": None, "genre": None}
    if len(parts) == 1:
        ans["genre"] = parts[0]
    else:
        ans["area"] = parts[0]
        ans["genre"] = parts[1]
    return pd.Series(ans)                 # 回傳 Series → 會變成多欄

total_df[["area", "genre"]] = total_df["area_genre"].apply(func)
```

### 觀念補充：Everything is an object（萬物皆物件）
課程一句重點：**所有東西都有「型態」，每種型態有自己的「操作」**。
- 型態 `dict` → 操作 `[key]`
- 型態 `list` → 操作 `[index]`、`.append()`
- **連「函式」本身也是一種物件**，可以被存進變數、被回傳：
```python
b = int          # 把「int 這個函式」存進 b（還沒執行）
b(4.6)           # 現在才執行 → 4
def test(a):
    return int if a > 5 else round   # 回傳「一個函式」
test(3)(4.6)     # test(3) 得到 round，再 (4.6) → 5
```
> 理解這個，就懂為什麼 `apply(func)` 是「把函式當作參數傳進去」。

## 補充：下載非文字檔（圖片）要用二進位 `wb`
```python
import urllib.request as req
content = req.urlopen("https://.../photo.jpg").read()
f = open("a.png", "wb")   # wb = write binary（圖片/影片是非純文字）
f.write(content)
f.close()
```
- 純文字檔：`"r"`/`"w"` + `encoding="utf-8"`。
- 非純文字（圖片/影片/壓縮檔）：`"rb"`/`"wb"`（不加 encoding）。

## 常見錯誤

- **字串沒轉數字就算術**：`"4.5" + 1` 會錯或變接字串。先 `.astype(float)`。
- **`concat` 後 index 重複**：需要時 `total_df = total_df.reset_index(drop=True)` 重編列號。
- **`apply` 的函式忘了 `return`**：整欄會變成 `None`。
- **過濾條件用 `and`/`or`**：pandas 多條件要用 `&`、`|`，且每個條件加括號：`df[(df.a>1) & (df.b<3)]`。
- **`glob` 路徑寫錯**：`*` 只比對一層；比對多層資料夾要逐層寫 `*/*`。

## 小練習

1. 讀入一個 CSV，用 `value_counts()` 找出出現最多次的 `userid`。
2. 新增一欄 `price_int`，把字串價格轉成整數（先想想怎麼去掉逗號/貨幣符號）。
3. 用過濾找出 `rating` 大於 4.0 的所有餐廳，存成新 CSV。

⬅ 上一章：[06 HTML 與 BeautifulSoup](06_html_beautifulsoup.md) ｜ ➡ 下一章：[08 Selenium 動態爬蟲](08_selenium.md)
