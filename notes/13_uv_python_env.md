# 13 · uv：Python 環境管理

> 對應課程：09/10~09/12（後半）
> 目標：懂「為什麼要管理 Python 環境」，會用 **uv** 建立獨立環境、安裝套件、與團隊同步。

## 重點摘要

不同專案可能需要**不同的 Python 版本、不同的套件版本**。若全部裝在一起會互相打架。**uv** 是新一代工具，能幫你「每個專案一個獨立環境」，並自動記錄版本，讓你（和團隊、和一年後的自己）都能重現一模一樣的環境。

## 核心觀念

### 1. 為什麼要管理環境？
- clone 別人的專案：要 Python 3.8？3.10？pandas 1.x？2.x？
- 團隊開發：大家版本要一致，程式才跑得起來。
- 同一台電腦上，Crawler / API / Airflow 需要的套件版本可能不同 → 各自獨立。

### 2. 有哪些工具？為什麼選 uv？
常見的有 `pip`、`venv`、`conda`、`pipenv`… 課程教 **uv**：
- **快**：用 Rust 寫的，比 pip 快 10–100 倍。
- **一站式**：一個工具取代 pip + venv + pip-tools。
- **現代**：自動記錄 Python 版本、套件版本（有 lock 檔、支援 `pyproject.toml`）。

## 一、安裝 uv 並建立環境

```bash
# 1) 安裝 uv（在 VSCode 終端機執行）
curl -LsSf https://astral.sh/uv/install.sh | sh
# 開一個「新的」終端機再確認
uv --version

# 2) 安裝指定版本的 Python
uv python list            # 看有哪些版本可裝
uv python install 3.11    # 安裝 Python 3.11（自動判定作業系統）

# 3) 建立這個專案要用的獨立環境（.venv）
uv venv --python=3.11

# 4) 初始化專案
uv init
```

### `uv init` 幫你生成的 5 個檔案
| 檔案 | 用途 |
|------|------|
| `.gitignore` | 告訴 git 哪些檔案「不要」上傳（如虛擬環境、快取） |
| `.python-version` | 指定此專案用的 Python 版本，確保團隊一致 |
| `pyproject.toml` | 專案核心設定：專案資訊、Python 版本、**套件相依** |
| `README.md` | 專案說明文件（做什麼、怎麼安裝執行） |
| `main.py` | 一段 Hello World 起手式 |

## 二、安裝套件與 lock 檔

```bash
uv add flask==3.1.0        # 安裝套件，並自動記進 pyproject.toml
```
- 套件清單記在 **`pyproject.toml`**。
- 精確的相依（含 flask 需要的其他套件）鎖在 **`uv.lock`**（類似 pipenv 的 `Pipfile.lock`）。
- 好處：**自動記錄 Python 版本 + 套件版本**——不記錄的話，一年後你一定忘記。

## 三、用獨立環境執行（重點觀念）

```bash
python                 # ← 可能用到「系統」的 Python，import flask 會失敗
uv run python          # ← 用專案獨立環境(.venv) 的 Python，import flask 成功
```
- 直接 `python` 有可能抓到別的環境。
- **`uv run python`** 才保證用當前專案 `.venv` 內的 Python。
- 同理跑腳本：`uv run python main.py`、跑 celery：`uv run celery ...`。

### 讓 VSCode 預設用這個環境
1. `Ctrl + Shift + P` → 輸入 `Python: Select Interpreter`。
2. 選剛剛建立的環境（名稱通常就是你的資料夾名，如 `test`）。
3. 沒出現就 `Ctrl + Shift + P` →「Reload Window」。
4. 開新終端機時會自動 `source .venv`，出現前綴代表已在獨立環境。
> 不同資料夾會用各自的獨立環境，互不干擾。

## 四、加入團隊：一鍵同步環境

當你加入一個用 uv 的團隊、clone 下專案後，只要一個指令就把「團隊需要的所有套件」裝好：
```bash
git clone https://github.com/TibameSam/crawler
cd crawler/
code .
uv sync                 # 依 pyproject.toml / uv.lock 安裝全部套件（約 3~5 分鐘）
```
> 這就是為什麼要有 `pyproject.toml` + `uv.lock`：**任何人 `uv sync` 就得到一模一樣的環境**。

## uv 對照舊工具（幫助理解）
| 你以前可能聽過 | uv 對應 |
|----------------|---------|
| `python -m venv` 建虛擬環境 | `uv venv` |
| `pip install X` | `uv add X` |
| `pip install -r requirements.txt` | `uv sync` |
| `python script.py` | `uv run python script.py` |
| `requirements.txt` | `pyproject.toml` + `uv.lock` |

## 常見錯誤

- **`uv --version` 找不到** → 安裝後要「開新的終端機」讓 PATH 生效。
- **`import` 套件失敗** → 你可能用了系統 python；改用 `uv run python`，或在 VSCode 選對 interpreter。
- **忘了 `uv sync`** → clone 別人專案後沒同步套件，當然跑不起來。
- **把 `.venv` 上傳 git** → 別傳！`.gitignore` 已排除，虛擬環境不該進版控。

## 小練習

1. 用 uv 建一個 3.11 環境、`uv init`，看看生成的 5 個檔案。
2. `uv add requests`，打開 `pyproject.toml` 看它被記在哪。
3. `uv run python` 進去 `import requests` 成功；再直接 `python` 試試差別。

⬅ 上一章：[12 Docker](12_docker.md) ｜ ➡ 下一章：[14 分散式爬蟲](14_distributed_crawler.md)
