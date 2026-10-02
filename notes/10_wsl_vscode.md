# 10 · WSL 與 VSCode 設定

> 對應課程：09/07
> 目標：在 Windows 上裝好 Linux(Ubuntu) 環境，並用 VSCode 連進去開發。（Mac 使用者可略過 WSL，本身就是類 Unix。）

## 重點摘要

- **WSL**＝Windows Subsystem for Linux，讓你在 Windows 裡跑一個真正的 **Ubuntu(Linux)**。
- 為什麼要 Linux？**業界服務都部署在 Linux**（GCP、AWS 的雲端機都是 Linux）。提早熟悉業界環境。
- **VSCode**＝微軟做的免費 IDE，可以在同一個介面寫 Python、用 git、操作 docker、輸入 linux 指令、AI 輔助。

## 一、安裝 WSL（Windows）

### 方法 A：一鍵安裝（推薦，較新系統）
以**系統管理員**開 PowerShell：
```powershell
wsl --install
```
重開機後，再執行：
```powershell
wsl --set-default-version 2
wsl --update
```

### 方法 B：手動開功能
1. 控制台 →「程式和功能」→「開啟或關閉 Windows 功能」。
2. 勾選 **「適用於 Linux 的 Windows 子系統」**。
3. 勾選 **「Hyper-V」** 或 **「虛擬機器平台」**。
4. 重新啟動電腦。
5. 到 **Microsoft Store** 搜尋 **Ubuntu** → 安裝 → 啟動，出現 Linux 畫面就成功了。

> 之後所有課程都在 Ubuntu 上進行。

### 建立一般使用者（不要用 root）
若啟動後是 `root` 身份，先加一個一般 user（`root` 權限太大，容易誤刪重要檔案）：
```bash
adduser test        # 建立名為 test 的使用者（設密碼時不會顯示，正常）
```
> Linux 帳號**不能用大寫**。

設定預設用一般使用者登入（在 Windows PowerShell）：
```powershell
ubuntu config --default-user your_name
```

## 二、安裝與設定 VSCode

1. 官網下載安裝：<https://code.visualstudio.com/>
2. VSCode 預設用 Windows 環境，要改成用 **Ubuntu(WSL)**：
   - 點左下角綠色圖示 →「**Connect to WSL / using Distro**」→ 選剛裝的 Ubuntu。
   - 成功後右下角顯示 **`WSL: Ubuntu`**。
3. 打開終端機：快捷鍵 **`` Ctrl + ` ``**，就進到 Linux 環境了。
4. 把終端機的預設指令處理器設成 Ubuntu 常用的 **bash**。

> VSCode 常用快捷：開設定面板 **`Ctrl + Shift + P`**（幾乎所有功能都從這裡叫出）。

## 三、一定要裝的 VSCode 插件（Extensions）

在左側 Extensions（積木圖示）搜尋安裝：

| 插件 | 用途 |
|------|------|
| **Python** | 讓 VSCode 變成 Python IDE（沒裝它，Python 功能不會啟用） |
| **Pylance** | Python 語法提示、分析、自動補全 |
| **Pylint** | 檢查是否符合 PEP 8（Python 標準寫作規範） |
| **autopep8** 或 **Black Formatter** | 自動排版程式碼（統一風格） |
| **Git Graph** | 視覺化 git 樹枝圖 |
| **Git History** | 看每行程式是誰、何時 commit 的 |
| **GitLens** | 強化 git 資訊（作者、blame 等） |
| Python Test Explorer（選用） | 測試工具，課程不強制 |

VSCode 的好處：
- **自動提示**：語法太多記不住，IDE 幫你補。
- **自動偵錯**：變數打錯、程式有問題，會出現「毛毛蟲」底線，滑鼠移過去看原因。
- **統一團隊工具/排版**：大家用同一套 formatter，協作更順。

## 為什麼不用 Spyder / Jupyter / Colab？
它們適合「單純寫 Python / 做筆記」，但 **VSCode 可以在同一個 IDE 同時做**：Python + git + docker + linux 指令 + AI 輔助 + 自動補全。做「系統」比較方便。（不過學基礎、做資料探索，Colab/Jupyter 仍然很好用——見[課程總覽](../README.md)。）

## 常見錯誤 / 疑難

- **WSL 裝不起來**：用系統管理員 PowerShell 跑 `wsl --install`，重開機後 `wsl --set-default-version 2`、`wsl --update`。
- **終端機是 root**：用 `ubuntu config --default-user your_name` 改一般使用者。
- **忘記 user 名稱**：終端機 `cd /home` 再 `ls`，出現的就是你的 user 名。
- **VSCode 還在 Windows 環境**：左下角切換到 `WSL: Ubuntu`，右下角要顯示才算成功。
- **Linux 帳號用大寫** → 不允許，請全小寫。

## 小練習

1. 裝好 WSL(Ubuntu)，在終端機輸入 `whoami` 確認你不是 root。
2. 讓 VSCode 右下角顯示 `WSL: Ubuntu`。
3. 裝好上表插件，隨便打錯一個變數名，觀察「毛毛蟲」提示。

⬅ 上一章：[09 架構圖與開發環境總覽](09_architecture_and_dev_env.md) ｜ ➡ 下一章：[11 Linux 指令與 Git 操作](11_linux_git.md)
