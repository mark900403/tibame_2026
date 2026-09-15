# 06 · HTML 與 BeautifulSoup（解析網頁）

> 對應課程：08/22（上午/下午）
> 需要套件：`urllib`（內建）、`beautifulsoup4`（`pip install beautifulsoup4`，程式裡 `import bs4`）

## 重點摘要

不是每個網站都有好用的 API。大多數時候我們要抓的是**網頁 HTML**，再用 **BeautifulSoup** 這個工具「解析」出想要的資料（名稱、價格、連結…）。本章用課程的「東京甜點餐廳排行(tabelog)」當範例。

## 核心觀念

### 1. HTML＝由「一個個區塊」組成的網頁
每個區塊長這樣：
```html
<a href="網址">顯示的文字</a>
 └名稱  └屬性        └內容    └結束
```
- **名稱(tag)**：決定「是什麼」。`a`＝超連結、`img`＝圖片、`video`＝影片、`div`＝一般區塊、`span`＝小段文字。
- **屬性(attribute)**：決定細節。連結的網址放在 `href`，圖片/影片的來源放在 `src`。
- **內容**：夾在中間、看得到的文字。

### 2. class 與 CSS 選擇器（怎麼「指定」要哪些區塊）
網頁用 **class** 屬性來分類、排版。爬蟲就靠 class 精準抓到目標。

```
標籤名   選它 → 用 tag：  a { }         （所有 a）
class   選它 → 加點 .： .price { }      （class 含 price 的）
id      選它 → 加井 #： #main { }       （id = main，整頁唯一）
```
- 一個區塊可以有多個 class：`class="c-rating c-rating--large"`。
- **id 是唯一的**（整頁只有一個），class 可以重複很多個。

### 3. 前端 vs 後端（背景知識）
- **前端**（你看得到的）：HTML(內容) + CSS(排版) + JavaScript(互動)。
- **後端**（伺服器）：收到請求 → 用程式處理（Python 的 Flask / Django / FastAPI）→ 查資料庫 → 回應。
- 爬蟲屬於「模擬前端去要資料」。

## 程式範例（逐行說明）

### (a) 抓網頁 + 加 headers 假裝成瀏覽器
有些網站會擋「不像瀏覽器」的請求，所以加 `User-Agent`：
```python
import urllib.request as req
import bs4 as bs

url = "https://github.com/Elwing-Chou/tibame_20260714/raw/refs/heads/main/baha.html"
h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/151 Safari/537.36"}
r = req.Request(url, headers=h)     # 帶著 headers 建立請求
f = req.urlopen(r)
content = f.read()

html = bs.BeautifulSoup(content)    # 把 HTML 交給 BeautifulSoup 解析
```
- `req.Request(url, headers=h)`：需要自訂 headers 時，先建立 Request 物件再 `urlopen`。
- `bs.BeautifulSoup(content)`：把一堆 HTML 文字變成「可以查詢的結構」。

### (b) find / find_all：找區塊
```python
# find_all(標籤, {屬性條件}) → 找出「全部」符合的（回傳 list）
for link in html.find_all("a"):
    link_href = link["href"]        # 取屬性：像 dict 一樣用 ["href"]
    text = link.get_text()          # 取內容文字
    if link_href.startswith("?sn"): # 篩選我們要的連結
        print("下載彈幕:", link_href)
```
- `find("tag", {"class": "xxx"})`：找**第一個**符合的。
- `find_all("tag", {"class": "xxx"})`：找**全部**，回傳 list，可 `for` 迴圈。
- 取**屬性**用 `區塊["href"]`；取**內容文字**用 `區塊.get_text()`。

### (c) 實戰：抓餐廳清單的多個欄位
```python
rs = html.find_all("div", {"class": "list-rst__body"})  # 每一間餐廳一個 div
for r in rs:
    # 先在「這一間」的區塊裡，找出各個小欄位
    name = r.find("a", {"class": "list-rst__rst-name-target"})
    rating = r.find("span", {"class": "c-rating__val"})
    prices = r.find_all("span", {"class": "c-rating-v3__val"})

    # 萃取：屬性用 [..]、文字用 get_text()，再用 strip() 去掉前後空白/換行
    name_text = name.get_text().strip()
    name_href = name["href"]
    rating_text = rating.get_text().strip()
    print(rating_text, name_text, name_href)
```
- **巢狀 find**：先 `find_all` 抓「每一間」的大區塊 `r`，再在 `r` 裡面 `find` 各欄位——這樣才不會把不同餐廳的資料混在一起。
- `strip()`：把字串前後多餘的空白、換行 `\n` 清掉。例：`"  a bc \n ".strip()` → `"a bc"`。

## 常見錯誤

- **class 名稱抄錯**：`find` 找不到會回傳 `None`，接著 `None.get_text()` 就爆 `AttributeError`。先確認 class 正確、或先判斷 `if name is not None`。
- **忘了先抓大區塊**：直接對整頁 `find_all` 各欄位，會把不同筆資料混在一起，數量也對不上。務必「先大區塊、再區塊內細找」。
- **屬性 vs 內容搞混**：網址在屬性 `["href"]`；顯示文字用 `get_text()`。
- **沒 `strip()`**：抓下來常有一堆空白/換行，之後分析會很亂。
- **被擋(403)**：加 `User-Agent`；有些站鎖地區 IP（見[第 05 章](05_web_crawling_api_json.md)）。

## 小練習

1. 抓一個網頁，印出頁面上所有連結（`a` 的 `href`）。
2. 從餐廳範例再多抓一個欄位（例如營業時間/地區），記得先 `find` 再 `get_text().strip()`。
3. 試著把 `find_all("div", {"class": "list-rst__body"})` 的數量印出來，看看一頁有幾間。

⬅ 上一章：[05 爬蟲：API 與 JSON](05_web_crawling_api_json.md) ｜ ➡ 下一章：[07 pandas 資料處理](07_pandas.md)
