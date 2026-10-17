# 11 · Linux 指令與 Git 操作

> 對應課程：09/10~09/12（前半）
> 目標：會用最基本的 Linux 指令在終端機移動、操作，並用 Git 把程式碼上傳 GitHub。

## 重點摘要

- 在 Linux（Ubuntu）裡，你用**指令**來移動資料夾、開檔案、下載專案。
- **Git** 是版本控制：記錄每次改動、能還原、能協作。GitHub 是放 git 專案的雲端平台。
- VSCode 有好用的 git 圖形介面，但**背後的指令也要會**（面試/沒有 GUI 時用得到）。

## 一、Linux 初學指令

| 指令 | 作用 | 範例 |
|------|------|------|
| `pwd` | 我現在在哪個資料夾 | `pwd` |
| `ls` | 列出當前資料夾內容 | `ls` |
| `cd 資料夾` | 進入資料夾 | `cd Class2025/` |
| `cd ..` | 回上一層 | `cd ..` |
| `cd`（不接） | 回到最外層(家目錄) | `cd` |
| `mkdir 名稱` | 新增資料夾 | `mkdir data` |
| `git clone 網址` | 下載 GitHub 專案到本地 | 見下 |
| `vim 檔案` | 文字編輯器 | 離開：先 `Esc`，再輸入 `:wq!` |
| `code .` | 用 VSCode 打開「當前資料夾」 | `code .` |

小技巧：
- **按 `Tab` 自動補齊**指令/路徑，少打字也少打錯。
- `whoami` 看自己是誰；`cd /home` + `ls` 可找出你的 user 名。

### 下載一個專案（clone）
```bash
git clone https://github.com/TibameSam/Class2025.git   # 複製 repo 要用 HTTPS 網址
cd Class2025/                                            # 進到專案資料夾
code .                                                   # 用 VSCode 打開它
```
> `code .` 很重要：VSCode 會針對「不同資料夾」記住不同的 git、Python 設定。

## 二、Git 基本流程（改東西 → 上傳）

Git 上傳的三步驟：**add（挑選改動）→ commit（拍快照＋寫訊息）→ push（上傳雲端）**。

```bash
git add test.py                 # 把改動的檔案「加入」這次要提交的清單
git commit -m "test"            # 拍一個快照，附上說明訊息
git push origin main            # 上傳到雲端 GitHub（有些舊 repo 是 master）
```

用 VSCode 圖形介面也能做同樣事：
1. 改檔案並存檔（`Ctrl + S`）→ 左側「Changes」出現變動。
2. 按 **`+`**（= `git add`）。
3. 輸入訊息 → 按 **Commit**（= `git commit -m`）。
4. 按 **Sync Changes**（= `git push`）上傳。

### 名詞：origin / main(master)
- `origin`：遠端（GitHub 雲端）的代稱。
- `main` 或 `master`：分支名稱。`origin/main` = 雲端上的 main 分支。

## 三、常見狀況：遠端和本地不同步

如果 push 失敗、或出現「兩個樹枝分支」，代表**雲端有你本地沒有的改動**，要先 `pull` 下來：
```bash
git config pull.rebase true     # 設定用 rebase 方式整併（樹枝較乾淨）
git pull                        # 把遠端拉下來合併
# 解決完再 push
git push origin main
```
- 若出現 **conflict（衝突）**：表示同一段被兩邊改過，需手動選擇保留哪個版本，改好後再 add/commit/push。

## 為什麼要上傳程式碼？
- **紀錄**：隨時可回到過去版本。
- **協作**：別人能拿到、一起開發。
- **進階**：接 **CI/CD**（自動化測試、自動部署到產品環境）。

## 常見錯誤

- **clone 用 SSH 但沒設金鑰** → 用 **HTTPS** 網址最省事。
- **忘了 `git add` 就 commit** → 沒東西被提交。先 add 再 commit。
- **push 被拒(rejected)** → 遠端有新東西，先 `git pull` 再 push。
- **`vim` 出不來** → `Esc` 後輸入 `:wq!`（存檔離開）或 `:q!`（不存離開）。
- **在錯的資料夾下指令** → 先 `pwd`/`ls` 確認位置（尤其 docker 指令要在專案資料夾內）。

## 小練習

1. `mkdir practice` → `cd practice` → `pwd` 確認你在裡面。
2. 在自己的 repo 新增一個檔案，用「add → commit → push」上傳，到 GitHub 網頁確認。
3. 故意在 GitHub 網頁改一次檔案，本地再 `git pull` 下來，體會同步流程。

⬅ 上一章：[10 WSL 與 VSCode 設定](10_wsl_vscode.md) ｜ ➡ 下一章：[12 Docker](12_docker.md)
