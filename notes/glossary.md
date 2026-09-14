# ✎ 名詞小字典（白話速查）

依主題分組。看筆記遇到不懂的詞，來這裡查。

## Python 基本
| 名詞 | 白話解釋 |
|------|----------|
| 變數 variable | 幫一個值取名字的「盒子」，用 `=` 指派 |
| `=` vs `==` | `=` 是「存進去」；`==` 是「是否相等」 |
| `%` 取餘數 | `7 % 2 = 1`；判斷奇偶用它 |
| `//` 整數除法 | 除完去小數，`7 // 2 = 3` |
| 縮排 indent | 前面的空白，用來表示「這段屬於誰」，通常 4 格 |
| 函式 function | 把一串步驟包成工具，用 `def` 定義，`return` 回傳 |
| 參數 argument | 函式的輸入值 |
| `None` | 「空的/沒有值」 |
| `float("inf")` | 無限大（`-inf` 負無限大），找極值的好起點 |

## 迴圈與遞迴
| 名詞 | 白話解釋 |
|------|----------|
| `for ... in` | 把一群東西逐一處理 |
| `range(n)` | 產生 0,1,...,n-1 |
| `while True` + `break` | 不確定次數的迴圈，條件到了跳出 |
| 遞迴 recursion | 函式呼叫自己，把大問題切小丟給「下一個人」 |
| 終止條件 base case | 遞迴一定要有的「不再切、直接回答」的情況 |
| 動態規劃 DP | 把算過的答案記起來，下次直接拿（空間換時間） |
| profiling | 實際量測程式跑多久（`time.time()` 前後相減） |

## 資料結構
| 名詞 | 符號 | 白話 |
|------|------|------|
| list 串列 | `[]` | 一排東西，用位置 `[i]` 取，從 0 開始 |
| dict 字典 | `{k:v}` | 用 key 查 value，描述複雜東西 |
| set 集合 | `{}`/`set()` | 不重複的一堆，能做交 `&`/聯 `\|`/減 `-` |
| tuple 元組 | `()` | 不可修改的一排，能當 dict key / set 元素 |
| Mutable/Unmutable | — | 可修改（list/dict/set）/ 不可修改（tuple/數字/字串） |
| 雙層 list | `l[i][j]` | list 裡還有 list；初始化用 `[[..] for _ in range(n)]` |
| list 生成式 | `[x for x in ...]` | 一行產生 list 的簡化寫法 |

## 爬蟲與網路
| 名詞 | 白話解釋 |
|------|----------|
| 爬蟲 crawler | 用程式代替人去網路抓資料 |
| Request/Response | 送出請求 / 伺服器回應 |
| API | 網站給「程式」用的資料網址，通常回 JSON |
| JSON | 文字資料格式，像 Python 的 list+dict 組合 |
| `json.loads` / `dump` | 字串→物件（讀）/ 物件→檔案（寫） |
| headers | 請求的附加資訊，如 `User-Agent`（假裝成瀏覽器） |
| User-Agent | 告訴伺服器「我是什麼瀏覽器」 |
| HTTP 狀態碼 | 2xx 成功、3xx 轉址、4xx 你有問題（403 被擋、404 找不到） |
| CSV | 逗號分隔的通用表格格式，Excel 可開 |
| `encoding="utf-8"` | 存讀檔支援中文 |
| `w`/`wb` | 寫純文字 / 寫二進位（圖片影片用 wb） |

## HTML / BeautifulSoup
| 名詞 | 白話解釋 |
|------|----------|
| HTML | 網頁的內容結構，由一個個「區塊(tag)」組成 |
| tag 標籤 | 區塊名稱：`a` 連結、`img` 圖、`div` 區塊、`span` 小段 |
| 屬性 attribute | 區塊細節：連結 `href`、圖片 `src` |
| class | 分類/排版用的屬性，可重複；選取時用 `.class` |
| id | 整頁唯一的識別，選取時用 `#id` |
| BeautifulSoup | 解析 HTML、幫你找區塊的工具（`import bs4`） |
| `find`/`find_all` | 找第一個 / 找全部符合的區塊 |
| `.get_text()` | 取區塊內的文字 |
| `.strip()` | 去掉字串前後的空白/換行 |
| 前端/後端 | 你看到的畫面(HTML/CSS/JS) / 伺服器處理(Flask/Django/FastAPI)+資料庫 |

## pandas
| 名詞 | 白話解釋 |
|------|----------|
| pandas | Python 的表格處理套件 |
| DataFrame | 會算術的「表格」型態 |
| Series | 表格中的「一欄」 |
| 過濾 filter | 用一排 True/False 挑出想要的「列」 |
| 布林遮罩 | `df["col"] == 值` 產生的一整排 True/False |
| 轉換 transform | 用 `apply(函式)` 改變/新增「欄」 |
| `to_csv`/`read_csv` | 寫出 / 讀入 CSV |
| `pd.concat` | 把多張表上下疊成一張 |
| `unique`/`value_counts` | 欄裡有哪些值 / 各出現幾次 |
| `.astype(float)` | 轉換整欄型態（字串→數字才能算） |
| 萬物皆物件 | 所有東西都有型態與操作；函式也是物件，可被傳遞 |

## Selenium
| 名詞 | 白話解釋 |
|------|----------|
| Selenium | 用程式「操作真的瀏覽器」，抓動態/需登入的網站 |
| driver | 被程式控制的瀏覽器 |
| `find_element(s)` | 找一個 / 找全部元素（對照 BS 的 find/find_all） |
| `.click()` / `.send_keys()` | 點擊 / 打字 |
| `.text` / `.get_attribute()` | 取文字 / 取屬性（對照 BS 的 get_text/[..]） |
| headless 無頭 | 不開視窗、在背景跑瀏覽器 |
| cookie | 存在瀏覽器的登入憑證；帶著它可免帳密登入 |

⬅ 回 [課程總覽](../README.md)
