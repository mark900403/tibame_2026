# 05 · 爬蟲入門：API 與 JSON

> 對應課程：08/06、08/22（前半）
> 需要套件：`urllib`（內建）、`json`（內建）、`pandas`（`pip install pandas`）、`os`（內建）

## 重點摘要

「爬蟲」就是**用程式代替人，去網路上把資料抓回來**。最簡單的一種是抓 **API**（網站專門給程式用的資料網址），拿回來的通常是 **JSON** 格式，再存成檔案或轉成表格。

本章用課程範例：抓「巴哈姆特動畫瘋」某支影片的**彈幕**資料。

## 核心觀念

### 1. 網路請求：送出（Request）→ 回應（Response）
你在瀏覽器打網址，其實是：你的電腦「送出請求」到伺服器，伺服器「回應」資料。程式做的是同一件事。

### 2. API 與 JSON
- **API**：伺服器提供給程式的網址，回傳的是「純資料」而不是網頁畫面。
- **JSON**：一種文字資料格式，長得就像 Python 的 **list + dict 組合**：
  ```
  {"data": {"danmu": [ {"userid": "abc", "text": "哈囉"}, {...} ]}}
  ```
  所以在 Python 裡，JSON 轉進來後就是**用 `[...]` 和 `["key"]` 一層層取值**。

## 程式範例（逐行說明）

### (a) 抓 API、把 JSON 轉成 Python 資料
```python
import json
import urllib.request as req      # 內建的「上網抓資料」工具，取個短名 req

url = "https://api.gamer.com.tw/anime/v1/danmu.php?videoSn=26850&geo=TW%2CHK"
f = req.urlopen(url)              # 送出請求、連到那個網址
content = f.read()               # 讀回內容（此時是 bytes 位元組）
content = json.loads(content)    # 把 JSON「文字」轉成 Python 的 dict/list

danmus = content["data"]["danmu"] # 一層層取值：data 裡的 danmu（是一個 list）
for d in danmus:                  # d 是每一則彈幕（dict）
    uid = d["userid"]
    text = d["text"]
    print(uid, text)
```
- `urlopen(url)`：開啟網址。
- `json.loads(...)`：**loads = load string**，把 JSON 字串 → Python 物件。
- 取值就是[第 03 章](03_data_structures.md)的 list/dict 操作：`["data"]["danmu"]` 再 `for` 迴圈。

### (b) 把資料存成 JSON 檔
```python
with open("test.json", "w", encoding="utf-8") as f:
    json.dump(danmus, f, ensure_ascii=False, indent=4)
```
- `with open(...) as f:`：開檔的標準寫法，區塊結束會自動關檔（比手動 `f.close()` 安全）。
- `"w"`：write 寫入模式；`encoding="utf-8"`：支援中文。
- `json.dump(資料, 檔案, ...)`：**dump = 存出**（對照 `loads` 是讀入）。
- `ensure_ascii=False`：中文正常顯示（不要變成 `\uXXXX`）。
- `indent=4`：漂亮縮排。

### (c) 轉成表格、存成 CSV（用 pandas）
**CSV**（Comma-Separated Values）是最通用的表格格式，用逗號分隔欄位，Excel 也能開。

```python
import pandas as pd
df = pd.DataFrame(danmus)        # 一個 [dict, dict, ...] 直接變成表格 DataFrame
df.to_csv("baha.csv", encoding="utf-8", index=False)  # 存成 CSV
df                                # 在 Colab/Notebook 會漂亮地顯示表格
```
- `pd.DataFrame([{...}, {...}])`：list of dict → 表格（每個 dict 是一列，key 是欄名）。
- `index=False`：不要把 pandas 自動加的列號寫進檔案。

### (d) 把「抓 + 存」包成函式（08/22）
實務上會把流程包成函式，方便重複抓不同影片，並自動建立資料夾：
```python
import os
def save_danmu_to_csv(sn, description=None):
    dirname = "baha" if description is None else f"baha/{description}"
    if not os.path.exists(dirname):     # 資料夾不存在
        os.makedirs(dirname)            # 就建立它
    url = f"https://api.gamer.com.tw/anime/v1/danmu.php?videoSn={sn}&geo=TW%2CHK"
    content = json.loads(req.urlopen(url).read())
    danmus = content["data"]["danmu"]
    df = pd.DataFrame(danmus)
    df.to_csv(f"{dirname}/{sn}.csv", encoding="utf-8", index=False)
    return df

save_danmu_to_csv("26850", "鬼滅")
```
- **f-string**：`f"...{sn}..."` 會把 `{sn}` 換成變數值，用來組網址/路徑很方便。
- `os.path.exists` / `os.makedirs`：檢查並建立資料夾。

## 補充：HTTP 狀態碼（伺服器的「回應代號」）
| 開頭 | 意思 | 常見 |
|------|------|------|
| 2xx | 成功 | 200 OK |
| 3xx | 轉址 | — |
| 4xx | 你(請求端)有問題 | 403 Forbidden（被擋，例如鎖海外 IP）、404 Not Found |

> 課程提到：巴哈鎖海外 IP，所以在 Colab（伺服器在國外）抓影片頁會 **403**。這不是你程式寫錯，是對方擋你。

## 常見錯誤

- **`json.loads` vs `json.dumps`**：`loads` 字串→物件（讀）、`dumps/dump` 物件→字串/檔案（寫）。
- **中文變亂碼**：存檔記得 `encoding="utf-8"`、`ensure_ascii=False`。
- **`index=False` 忘了加**：CSV 會多一欄沒用的列號。
- **403/404**：先確認網址對不對、對方是否擋 IP，再考慮加 headers（見[第 06 章](06_html_beautifulsoup.md)）。

## 小練習

1. 換一個 `videoSn` 抓另一支影片的彈幕，存成 CSV。
2. 只把每則彈幕的 `text` 收集成一個 list，印出前 10 筆。
3. 用 `len(danmus)` 看看這支影片總共有幾則彈幕。

⬅ 上一章：[04 pygame 翻牌遊戲](04_pygame_game.md) ｜ ➡ 下一章：[06 HTML 與 BeautifulSoup](06_html_beautifulsoup.md)
