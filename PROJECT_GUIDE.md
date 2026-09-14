# ★ 專題步驟指南（資料處理專題）

這份指南把課程學到的東西，串成一個**完整的資料處理專題流程**，並用新手看得懂的步驟一步步帶你做。

專題的標準流程（也是這門課的主線）：

```
① 定題目 → ② 抓資料(爬蟲) → ③ 存檔 → ④ 整理清理(pandas) → ⑤ 分析 → ⑥ 視覺化 → ⑦ 報告
```

> ⚠ 我還不知道你的**專題題目**是什麼。下面先給一個「通用範本」＋一個「具體示範（東京甜點餐廳排行）」，你只要把資料來源換成你的題目即可。做到後面把你的題目告訴我，我可以幫你把每一步的程式碼補成你的版本。

---

## Step 0：環境準備（只做一次）

1. 決定用 **Google Colab**（推薦新手，免安裝）或本機 Python。
2. 需要的套件（Colab 多半已內建；本機用 `pip install`）：
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib
   # 若要動態爬蟲再加： pip install selenium undetected-chromedriver
   ```
3. 新開一個 `.ipynb`，第一格先 `import` 會用到的套件。

✅ 完成標準：能 `import pandas as pd` 不報錯。

---

## Step 1：定題目與「要哪些欄位」

先想清楚**最後想回答什麼問題**，反推需要哪些資料欄位。

- 例：問題「東京哪些甜點店評分最高、價位如何？」→ 欄位：`店名、評分、地區、類型、午餐價、晚餐價、連結`。
- 寫下**資料來源網址**與**每一欄對應網頁的哪個區塊/class**。

✅ 完成標準：一張「欄位清單」+ 一個資料來源網址。

參考：[06 HTML 與 BeautifulSoup](notes/06_html_beautifulsoup.md)

---

## Step 2：先抓「一頁 / 一筆」成功（最重要的一步）

**不要一開始就想抓全部**。先確定「抓一頁、印出來對不對」。

- 若來源是 **API（回 JSON）** → 用 [05 章](notes/05_web_crawling_api_json.md)：`urllib` + `json.loads`。
- 若來源是 **一般網頁（HTML）** → 用 [06 章](notes/06_html_beautifulsoup.md)：`urllib` + BeautifulSoup。

示範（HTML，先抓一頁、只 `print` 不存檔）：
```python
import urllib.request as req
import bs4 as bs

url = "https://tabelog.com/tw/tokyo/rstLst/sweets/?SrtT=rt"
html = bs.BeautifulSoup(req.urlopen(url).read())

rs = html.find_all("div", {"class": "list-rst__body"})   # 先抓「每一間」的大區塊
print("這一頁有幾間：", len(rs))                          # 先確認數量對不對
r = rs[0]                                                 # 先只看第一間
name = r.find("a", {"class": "list-rst__rst-name-target"}).get_text().strip()
rating = r.find("span", {"class": "c-rating__val"}).get_text().strip()
print(name, rating)
```

✅ 完成標準：能正確印出**第一筆**的幾個欄位。

> 卡關提示：`find` 回 `None` → class 抄錯或該筆沒有這欄。先 `print(r)` 看原始 HTML 對照。

---

## Step 3：把「一頁全部」變成結構化資料（list of dict）

一間店 = 一個 dict；一頁 = 一個 list。這是為了下一步進 pandas。

```python
def parse_page(html):
    table = []
    for r in html.find_all("div", {"class": "list-rst__body"}):
        data = {
            "name":   r.find("a", {"class": "list-rst__rst-name-target"}).get_text().strip(),
            "rating": r.find("span", {"class": "c-rating__val"}).get_text().strip(),
            "link":   r.find("a", {"class": "list-rst__rst-name-target"})["href"],
        }
        table.append(data)
    return table
```

✅ 完成標準：`parse_page(html)` 回傳一個「list，裡面是每筆的 dict」。

參考：[03 資料結構](notes/03_data_structures.md)、[05 章存檔觀念](notes/05_web_crawling_api_json.md)

---

## Step 4：擴大到「多頁」並合併（迴圈 + 函式）

把「抓一頁」包成函式，用迴圈跑很多頁，每頁做成 DataFrame，最後 `concat`。

```python
import pandas as pd

def download_page(page):
    url = f"https://tabelog.com/tw/tokyo/rstLst/sweets/{page}/?SrtT=rt"
    html = bs.BeautifulSoup(req.urlopen(url).read())
    return pd.DataFrame(parse_page(html))

frames = []
for i in range(10):            # 先抓 10 頁；建議從 range(2) 開始測
    frames.append(download_page(i + 1))
total_df = pd.concat(frames).reset_index(drop=True)
total_df.head()
```

✅ 完成標準：一張含多頁資料的大表 `total_df`。

> 禮貌與安全：頁數別一次拉太大；必要時每頁之間 `time.sleep(1)`，避免對網站造成負擔或被擋（[05 章 403 說明](notes/05_web_crawling_api_json.md)）。

參考：[01 迴圈/函式](notes/01_python_basics.md)、[07 pandas](notes/07_pandas.md)

---

## Step 5：存檔（先把「生資料」存起來）

先把原始抓到的資料存一份 CSV，之後清理都從檔案讀，**不用每次重爬**。
```python
total_df.to_csv("raw_data.csv", encoding="utf-8", index=False)
df = pd.read_csv("raw_data.csv", encoding="utf-8")
```

✅ 完成標準：資料夾裡有 `raw_data.csv`，且能重新 `read_csv` 回來。

---

## Step 6：清理與轉換（pandas 兩大操作）

這步把「髒資料」變乾淨、變可分析。常見工作：

1. **型別轉換**：把字串數字轉成數字才能算。
   ```python
   df["rating"] = df["rating"].astype(float)
   ```
2. **欄位拆解**（用 `apply` 回傳 `pd.Series`）：把 `"地區 / 類型"` 拆兩欄。
   ```python
   def split_ag(s):
       parts = str(s).split(" / ")
       return pd.Series({"area": parts[0] if len(parts) > 1 else None,
                         "genre": parts[-1]})
   df[["area", "genre"]] = df["area_genre"].apply(split_ag)
   ```
3. **過濾**（布林遮罩）：留下想要的列。
   ```python
   good = df[df["rating"] >= 4.0]
   ```

✅ 完成標準：欄位型別正確、沒有明顯髒值、能算出基本統計 `df.describe()`。

參考：[07 pandas 資料處理](notes/07_pandas.md)

---

## Step 7：分析

用 pandas 回答你 Step 1 的問題：
```python
df["genre"].value_counts()             # 各類型數量
df.groupby("area")["rating"].mean()    # 各地區平均評分
df.sort_values("rating", ascending=False).head(10)   # 評分前 10 名
```

✅ 完成標準：能用 1–3 個數字/表格回答你的核心問題。

---

## Step 8：視覺化（matplotlib）

把結論畫成圖，報告更有說服力。
```python
import matplotlib.pyplot as plt
top = df.sort_values("rating", ascending=False).head(10)
plt.barh(top["name"], top["rating"])   # 橫向長條圖
plt.title("Top 10 rating")
plt.tight_layout()
plt.show()
```
> 中文顯示需另設中文字型，否則會出現方框；先用英文標題也可以。

✅ 完成標準：至少一張能說明結論的圖。

參考：[02 章 matplotlib 入門](notes/02_recursion_dp.md)

---

## Step 9：整理成報告 / 專題成果

建議結構：
1. **題目與動機**（想回答什麼）
2. **資料來源與方法**（哪個網站、抓了哪些欄位、幾筆）
3. **清理過程**（做了哪些轉換、遇到什麼髒資料）
4. **分析結果 + 圖表**
5. **結論與限制**（資料的偏誤、樣本大小、可以再做什麼）

✅ 完成標準：別人只看你的報告，就能懂你做了什麼、得到什麼。

---

## 進階分支（依你的題目才需要）

- 資料**要登入 / JS 才出現** → 改用 [08 Selenium](notes/08_selenium.md)。
- 要**下載圖片/檔案** → [07 章「二進位 wb」](notes/07_pandas.md)。
- 資料**很多來源檔** → `glob` + `concat`（[07 章](notes/07_pandas.md)）。

---

## 新手常見卡關對照表

| 症狀 | 可能原因 | 看哪裡 |
|------|----------|--------|
| `find` 得到 `None` 後爆錯 | class 抄錯 / 該筆沒這欄 | [06 章](notes/06_html_beautifulsoup.md) |
| 中文變亂碼 | 沒設 `encoding="utf-8"` | [05 章](notes/05_web_crawling_api_json.md) |
| 數字不能算/相加變接字串 | 還是字串，沒 `astype` | [07 章](notes/07_pandas.md) |
| 抓下來被擋 403 | 沒 headers / 對方鎖 IP | [05](notes/05_web_crawling_api_json.md)、[06 章](notes/06_html_beautifulsoup.md) |
| `IndentationError` | 縮排不一致 | [01 章](notes/01_python_basics.md) |
| CSV 多一欄怪列號 | 忘了 `index=False` | [05](notes/05_web_crawling_api_json.md)、[07 章](notes/07_pandas.md) |

---

## 下一步（給我資訊，我幫你客製）

把這幾點告訴我，我可以把上面每一步的程式碼直接改成**你的專題版本**：
1. 你的**專題題目 / 想回答的問題**是什麼？
2. **資料來源**（網站網址，或是否有 API）？需要登入嗎？
3. 你想要的**最終產出**（一份報告？幾張圖？一個乾淨的 CSV？）
4. 交作業的**格式/期限**限制（如果有）。

⬅ 回 [課程總覽](README.md)
