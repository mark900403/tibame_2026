# 04 · pygame 翻牌（記憶配對）遊戲

> 對應課程：07/25（後半）、07/28
> 需要套件：`pygame`（`pip install pygame`）、`random`（內建）
> 這章是「綜合應用」：把雙層 list、dict/set、迴圈、函式全部用上。做小遊戲不是重點，**練習用資料結構描述狀態**才是重點。

## 重點摘要

用 pygame 做一個 8×8 的翻牌配對遊戲：點兩張牌，數字一樣就配對成功。核心是把「遊戲狀態」用**兩個雙層 list**描述：
- `board_nums[i][j]`：每格的數字。
- `board_pair[i][j]`：每格是否已配對（`True/False`）。

## 核心觀念

### 1. 遊戲程式的三大區塊
- **常數/設定**：格子大小、字型、視窗尺寸。
- **邏輯(LOGIC)**：資料怎麼存、配對規則。
- **畫面(UI)**：把資料畫成看得到的圖 + 收滑鼠/鍵盤事件。

### 2. 座標轉換：畫面(x,y) ↔ 邏輯(i,j)
- 畫面用「像素座標」`(x, y)`，`x` 往右、`y` 往下。
- 邏輯用「第幾列第幾欄」`(i, j)`，`i` 對應 `y`、`j` 對應 `x`。
- 換算：`i = y // inter - 1`、`j = x // inter - 1`（`inter` 是每格像素、`-1` 是因為留了一圈邊）。

### 3. 遊戲主迴圈（event loop）
遊戲要「一直跑不能結束」，所以用 `while running:`，每圈去收使用者事件（點擊、關視窗）。

## 程式重點（節錄 + 說明）

### (a) 初始化棋盤數字：把位置洗牌後兩兩配同一個數字
```python
import random
NOT_PAIR, PAIR = False, True
col, row = 8, 8

board_nums = [[None] * col for i in range(row)]     # 每格數字（先都 None）
board_pair = [[NOT_PAIR] * col for i in range(row)] # 每格是否配對（先都 False）

# 把所有 (i, j) 收集起來、洗牌
total_pos = []
for i in range(row):
    for j in range(col):
        total_pos.append((i, j))
random.shuffle(total_pos)      # 隨機打亂

# 兩兩取出位置，填入「同一個、且沒用過」的數字
already = set()                # 用 set 記錄用過的數字（避免重複）
while len(total_pos) > 0:
    i1, j1 = total_pos.pop()   # pop() 從尾端取出一個
    i2, j2 = total_pos.pop()
    while True:
        n = random.randint(1, 100)
        if n not in already:   # 沒用過才用
            already.add(n)
            board_nums[i1][j1] = n
            board_nums[i2][j2] = n
            break
```
看得出來嗎？這裡把 **tuple**（位置 `(i,j)`）、**set**（`already` 去重）、**雙層 list**（棋盤）全用上了。

### (b) 主迴圈 + 滑鼠配對邏輯（重點觀念，非完整）
```python
i_prev, j_prev = None, None    # 記住「上一張被點的牌」

running = True
while running:
    for event in pg.event.get():           # 收取所有事件
        if event.type == pg.MOUSEBUTTONUP: # 放開滑鼠
            x, y = pg.mouse.get_pos()
            i, j = y // inter - 1, x // inter - 1   # 畫面座標→邏輯座標

            if board_pair[i][j] == NOT_PAIR:        # 還沒配對的格子才處理
                if i_prev is None:                  # 這是第一張
                    pass
                elif (i, j) == (i_prev, j_prev):     # 點到同一張，不算
                    pass
                elif board_nums[i][j] == board_nums[i_prev][j_prev]:
                    board_pair[i][j] = PAIR          # 數字相同 → 兩張都配對
                    board_pair[i_prev][j_prev] = PAIR
                i_prev, j_prev = i, j                # 更新「上一張」
            draw()                                   # 依最新狀態重畫
        if event.type == pg.QUIT:                    # 按視窗 x
            running = False
pg.quit()
```

### (c) 判斷勝利：所有格子都配對了
```python
def check_win():
    for i in range(row):
        for j in range(col):
            if board_pair[i][j] == NOT_PAIR:
                return False      # 只要還有一格沒配對就沒贏
    return True
```

### (d) 把重複的初始化包成 `reset()`
課程後面把「洗牌+填數字」包成一個 `reset()` 函式，贏了就呼叫它重新開局——這就是[第 01 章](01_python_basics.md)「函式＝可重複使用的工具」的實際好處。

## 常見錯誤

- **雙層 list 用 `[[NOT_PAIR]*col]*row`（錯！）**：會所有列共用，改一格全變。要用 `[[NOT_PAIR]*col for i in range(row)]`（見[第 03 章](03_data_structures.md)）。
- **i/j 與 x/y 對調**：記住 `i` 配 `y`、`j` 配 `x`，弄反畫面會整個轉向。
- **忘記重畫 `draw()`**：改了資料卻沒重畫，畫面不會更新。
- **少了事件迴圈或 `pg.quit()`**：視窗會沒反應或關不掉。

## 小練習

1. 把棋盤改成 4×4，觀察哪些變數要改（提示：只要改 `col, row`）。
2. 加一個「步數」計數器，每點一次 +1，贏了印出總步數。
3. 想一想：如果要做「花色配對」而不是數字，`board_nums` 要改成存什麼？

⬅ 上一章：[03 資料結構](03_data_structures.md) ｜ ➡ 下一章：[05 爬蟲：API 與 JSON](05_web_crawling_api_json.md)
