# 02 · 遞迴與動態規劃(DP)

> 對應課程：07/21、07/23
> 需要套件：`time`（內建）、`matplotlib`（畫圖，選讀）

## 重點摘要

- **遞迴（recursion）**：一個函式「呼叫自己」，把大問題切成小問題丟給「下一個人」做。
- **動態規劃（DP, Dynamic Programming）**：把「算過的答案記錄起來」，下次遇到直接拿，用**空間換時間**。
- 兩者常一起出現：先用遞迴把問題寫出來，再加「記錄」變快。

## 核心觀念

### 1. 遞迴＝「我只做一小步，其他丟給別人」
課程用一個很生動的比喻：老師叫你算 `1+2+...+10`，你很懶，只想自己做「加 1」，剩下的 `2+...+10` 丟給下一個同學；他也只做「加 2」，再丟給下一個…直到最後一個同學遇到「只剩一個數」就直接回答（**不偷懶＝終止條件**）。

```python
def add(start, end):
    # 終止條件：問題小到不用再切（頭尾一樣，只有一個數）
    if start == end:
        return end
    # 遞迴：自己只做 start，其餘丟給「下一個人」
    else:
        other = add(start + 1, end)   # 呼叫自己，處理 start+1 ~ end
        return start + other

print(add(1, 5))   # 15
```

### 2. 遞迴 SOP（照這個模板想就對了）

```
def 函式(參數):
    if 不逃避（問題太簡單，直接回答）:
        return 答案
    else 逃避（把原問題切成更小的同型問題）:
        丟給自己 → 拿到小問題的答案 → 補上我這一步 → return
```

- **一定要有終止條件**，否則會「無限遞迴」（`RecursionError`）。
- 每次遞迴呼叫，問題要**變小**，才會朝終止條件靠近。

### 3. 經典遞迴範例：河內塔
把 `n` 個盤子從 A 移到 C（一次一個、大不能疊小上）。想法：先把上面 `n-1` 個搬走 → 搬最大的那個(1 步) → 再把 `n-1` 個搬回來。

```python
def hanoi(n):
    if n == 1:
        return 1
    else:
        return hanoi(n - 1) + 1 + hanoi(n - 1)   # = 2*hanoi(n-1)+1

print(hanoi(3))   # 7
```

## 動態規劃(DP)：用「記錄」加速

### 為什麼需要？
算柯拉茲最大值時，`7 → 22 → 11 → ... → 5 → 16 → 8 → 4 → 2 → 1`。如果我**之前已經算過 5** 的答案，走到 5 時就不必再往下走了——直接拿舊答案。

### (a) 迴圈 + 記錄字典（record）

```python
record = {}          # 記錄：{某個數: 它的柯拉茲最大值}

def return_collatz_max_dp(n):
    n_copy = n                 # 先把原本的 n 記下來（等等要當 key）
    maxv = float("-inf")
    while True:
        if n in record:        # 這個 n 以前算過 → 直接用，提早結束
            maxv = max(maxv, record[n])
            break
        maxv = max(maxv, n)
        if n == 1:
            break
        if n % 2 == 1:
            n = n * 3 + 1
        else:
            n = n // 2
    record[n_copy] = maxv       # 把答案存起來，下次別人可以用
    return maxv
```

- `record` 是一個 **dict（字典）**：用 `key`（原本的數）查 `value`（最大值）。
- `if n in record:` 檢查「這個數是不是算過了」。
- **關鍵**：一定要用 `n_copy` 記住「一開始的 n」，因為 `n` 在迴圈裡會被改掉。

### (b) 遞迴 + 記錄（標準 DP 寫法）

```python
record = {}
def return_collatz_max_dp(n):
    if n == 1:                       # 終止條件
        return 1
    elif n in record:                # 已算過 → 直接回傳（這就是 DP 的核心）
        return record[n]
    else:
        if n % 2 == 0:
            other = return_collatz_max_dp(n // 2)
        else:
            other = return_collatz_max_dp(3 * n + 1)
        ans = max(n, other)
        record[n] = ans              # 存起來
        return ans
```

### (c) 量測速度（profiling）
用 `time.time()` 取得「現在時間」，前後相減就是花費秒數。

```python
import time
start_t = time.time()

result = {}
for i in range(1000000):     # 算 1~100萬 的柯拉茲最大值
    n = i + 1
    result[n] = return_collatz_max_dp(n)

end_t = time.time()
print("時間是:", end_t - start_t, "秒")
```

有沒有加 `record` 那一行（DP 開關），速度會差非常多——這就是「用空間換時間」。

### (d) 把結果畫出來（matplotlib）

```python
import matplotlib.pyplot as plt
x, y = [], []
for i in range(2, 10000):
    x.append(i)
    y.append(result[i])
plt.plot(x, y)      # x 當橫軸、y 當縱軸畫折線
plt.show()          # 顯示圖
```

## 常見錯誤

- **忘記終止條件 / 問題沒變小** → `RecursionError: maximum recursion depth exceeded`。
- **DP 忘了記住原始 key**：`n` 在過程被改了，存 `record[n]` 會存錯。用 `n_copy`。
- **以為 DP 一定要遞迴**：迴圈也能做 DP，重點是「把算過的存起來」。
- **`range(1000000)` 很大**：先用小數字（如 100）測試對不對，再放大。

## 小練習

1. 用遞迴寫 `factorial(n)`（階乘 `n!`）。終止條件是什麼？
2. 把河內塔改成「印出每一步怎麼搬」（提示：多傳 `from/to/via` 三根柱子）。
3. 把柯拉茲 DP 的「記錄那一行」註解掉，用 `time` 比較有無 DP 的秒數差異。

⬅ 上一章：[01 Python 基礎](01_python_basics.md) ｜ ➡ 下一章：[03 資料結構](03_data_structures.md)
