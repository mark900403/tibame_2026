# 08 · Selenium 動態爬蟲（操作瀏覽器）

> 對應課程：08/28（後半）
> 需要套件：`selenium`、`undetected-chromedriver`（`pip install selenium undetected-chromedriver`）；需要安裝 Chrome 瀏覽器

## 重點摘要

有些網站的內容是**打開後靠 JavaScript 才長出來的**，或是需要**登入、點按鈕、捲動**才看得到。這時單純用 `urllib` 抓「原始 HTML」是抓不到的——要改用 **Selenium**：它會**真的開一個瀏覽器**，讓程式像真人一樣操作。

## 核心觀念

### 1. 什麼時候用 Selenium？（vs BeautifulSoup）
| 情況 | 用哪個 |
|------|--------|
| 資料在原始 HTML 裡、或有 API | `urllib` + BeautifulSoup（[第 05](05_web_crawling_api_json.md)、[06 章](06_html_beautifulsoup.md)）→ **快** |
| 內容要 JS 才出現、要登入/點擊/捲動 | **Selenium**（開真瀏覽器）→ 慢但萬能 |

### 2. 兩套「找元素」的語法對照
你在[第 06 章](06_html_beautifulsoup.md)學的 BeautifulSoup，和 Selenium 的對照：

| 動作 | BeautifulSoup | Selenium |
|------|---------------|----------|
| 找一個 | `find(...)` | `driver.find_element(By.XXX, "...")` |
| 找全部 | `find_all(...)` | `driver.find_elements(By.XXX, "...")` |
| 取文字 | `.get_text()` | `.text` |
| 取屬性 | `["href"]` | `.get_attribute("href")` |
| 額外能做 | — | `.click()` 點擊、`.send_keys()` 打字 |

## 程式範例（逐行說明）

### (a) 開瀏覽器、搜尋、抓結果
```python
import time
import undetected_chromedriver as uc         # 較不易被網站偵測的 Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = uc.Chrome(version_main=152, use_subprocess=False)  # 開一個 Chrome
driver.get("https://www.google.com/")        # 前往網址
driver.maximize_window()                       # 視窗最大化

e = driver.find_element(By.CLASS_NAME, "gLFyf")  # 找搜尋框（用 class 名）
e.send_keys("chiikawa")                        # 像鍵盤一樣「打字」
e.send_keys(Keys.ENTER)                        # 按 Enter 送出
time.sleep(3)                                  # 等 3 秒讓結果載入（重要！）

es = driver.find_elements(By.CLASS_NAME, "zReHs")  # 找「全部」搜尋結果
for e in es:
    print(e.text)                              # 標題文字
    print(e.get_attribute("href"))             # 連結網址
```
- `By.CLASS_NAME` / `By.ID` / `By.CSS_SELECTOR`…：告訴 Selenium「用什麼方式找」。
- `time.sleep(3)`：Selenium 常需要「等網頁反應」，不等可能會找不到還沒出現的元素。
- `.click()`（點擊）與 `.send_keys()`（打字）是 Selenium 才有的互動能力。

### (b) 用 cookie 免帳密登入（觀念，需自備 cookie）
```python
driver.get("https://www.facebook.com/")
cookie_s = "自己補"                            # 從瀏覽器開發者工具複製你的登入 cookie
for cookie in cookie_s.split(";"):
    k, v = cookie.split("=", maxsplit=1)
    driver.add_cookie({"name": k.strip(), "value": v.strip()})
driver.get("https://www.facebook.com/")        # 重新載入 → 已是登入狀態
time.sleep(5)
```
> 觀念：帶著你的登入 cookie，網站就以為是「已登入的你」。**只用在自己的帳號、合法用途**。

## ⚠ 重要：環境與注意事項

- Selenium 要**在有桌面的環境**跑（會開瀏覽器視窗）；純命令列/雲端要用「無頭模式 headless」或設定虛擬顯示。Colab 直接跑 GUI 版會比較麻煩。
- `version_main=152` 要對應**你電腦的 Chrome 大版本**，不然會啟動失敗。
- 遇到 `No module named distutils`：課程提示 `pip install --upgrade setuptools`。

## 常見錯誤

- **沒等就找元素**：頁面還沒載完 → 找不到。加 `time.sleep()`，或學 `WebDriverWait`（進階、更穩）。
- **class/選擇器變動**：大網站的 class 常變，抓不到要重新查看網頁原始碼。
- **Chrome 版本不合**：`version_main` 要對上你的 Chrome 版本。
- **把 Selenium 當萬用**：能用 API/BeautifulSoup 就別用 Selenium（慢很多）。
- **合法與禮貌**：遵守網站條款、放慢速度（`sleep`）、不要爬取或散布私人/受保護資料。

## 小練習

1. 用 Selenium 打開一個網站，抓下標題列 `driver.title` 印出來。
2. 把 (a) 的搜尋關鍵字改成你想搜的，收集前 10 筆標題與連結。
3. 想一想：你的專題資料，是屬於「BeautifulSoup 就能抓」還是「非 Selenium 不可」？

⬅ 上一章：[07 pandas 資料處理](07_pandas.md) ｜ ➡ [名詞小字典](glossary.md) ｜ [專題步驟指南](../PROJECT_GUIDE.md)
