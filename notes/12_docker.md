# 12 · Docker（容器化）

> 對應課程：09/10~09/12、09/14（打包與 network）
> 目標：懂 Docker 的三大概念，會用 docker 指令與 docker-compose 一鍵啟動服務，會寫 Dockerfile 把程式打包成 image。

## 重點摘要

**Docker** 解決一句話的痛：**「在我電腦可以跑，在別人機器不行」**。它把「程式 + 執行環境」一起打包成獨立的盒子（容器），到哪都一樣能跑。後續課程的 RabbitMQ、Flower、MySQL、Airflow 全靠 Docker「一鍵部署」。

## 核心觀念：三個關鍵字

| 名詞 | 比喻 | 說明 |
|------|------|------|
| **Image 映像檔** | 光碟 / 安裝檔 | 打包好的環境模板（含 Ubuntu、Python、MySQL…）。從 Docker Hub 下載 |
| **Container 容器** | 用光碟裝好、正在跑的程式 | 用 Image 建立出來的「獨立執行環境」，不受你電腦環境影響 |
| **Volume 資料卷** | 外接硬碟 | 把容器內的資料連到本機硬碟，容器關掉資料也不會不見 |

- **Docker Hub**（<https://hub.docker.com/>）：類似 GitHub，是大家分享 Image 的地方。
- **一個 Image 可以建立很多個 Container**。

## 一、安裝與第一個容器

1. 安裝 **Docker Desktop**（Windows/Mac，官方安裝頁；**不要選 Linux 版**）。
2. 註冊 / 登入 Docker 帳號。
3. 在 VSCode 終端機測試：
```bash
docker ps        # 列出「還在跑」的容器；能執行代表 docker 正常
```

### 跑第一個 image：hello-world
```bash
docker pull hello-world:latest   # 從 Docker Hub 下載 image
docker run hello-world           # 用 image 建立並執行 container
```

### 權限問題（Linux/WSL 常見）
若出現 `permission denied`：
```bash
sudo usermod -aG docker $USER    # 把自己加入 docker 群組（$USER 是目前使用者）
# 然後「重開 terminal」；若還是不行，重開機通常可解決
```

## 二、常用 docker 指令

| 指令 | 作用 |
|------|------|
| `docker ps` | 列出「執行中」的容器 |
| `docker ps -a` | 列出「所有」容器（含已停止） |
| `docker images` | 列出本機的 image |
| `docker pull 名稱` | 下載 image |
| `docker run 名稱` | 用 image 建立並啟動容器 |
| `docker logs 容器名` | 看容器的 log（**看 log 是工程師必備技能**，看不懂就貼給 AI） |
| `docker rmi 名稱` | 刪除 image（省硬碟空間） |

互動式進入一個乾淨容器測試（很好用）：
```bash
docker run -it --rm ubuntu:22.04 bash
# run: 啟動新容器  -it: 進到容器裡  --rm: 關掉就自動刪除  bash: 進去後開一個終端機
# 環境弄爛了就 exit 離開，再跑一次 → 從乾淨環境重來
```

## 三、docker-compose：一次管理「多個」容器

- `docker run`：啟動**一個**容器。
- **docker-compose**：用一個 `.yml` 設定檔，一次管理**多個**容器（工作上一定會同時用很多服務）。

```bash
docker compose version                    # 確認可用
docker compose -f rabbitmq.yml up -d      # 依 yml 啟動服務（-d 背景執行）
docker compose -f rabbitmq.yml down       # 依 yml 關閉服務
```
> `-f` 指定要用哪個 yml 檔；`up -d` 啟動、`down` 關閉。
> 若 `docker compose` 不可用（Ubuntu）：`sudo apt-get install docker-compose-plugin`。

### yml 檔在寫什麼？（rabbitmq.yml 為例）
一個 compose yml 描述「要啟動哪些服務、各自用什麼 image、開哪些 port、設哪些環境變數」：
- **service name**：服務名稱（也是容器在內網的「主機名」，很重要，見下方 network）。
- **image**：用哪個映像檔部署。
- **ports**：容器內外連通的管道（例如把容器的 5672 對到本機 5672）。
- **environment**：環境變數（帳號、密碼、host）。
- **depends_on / command**：啟動順序、初始化指令（例如 flower 要等 rabbitmq 起來）。

## 四、把「自己的程式」打包成 Image（Dockerfile）

本地能跑還不夠，產品環境也要能跑——把程式與環境寫進 **Dockerfile**，build 成 image。

### Dockerfile 常用指令
| 指令 | 作用 |
|------|------|
| `FROM` | 以哪個 image 為基底（例：`FROM ubuntu:22.04`） |
| `RUN` | 建置時執行指令（安裝工具、套件） |
| `COPY` | 把本機檔案複製進 image |
| `ENV` | 設定環境變數 |
| `WORKDIR` | 設定工作目錄 |
| `CMD` | 容器**啟動時**預設執行的指令 |

範例（觀念示意，對應課程爬蟲）：
```dockerfile
FROM ubuntu:22.04                     # 從乾淨的 ubuntu 開始
RUN apt-get update && apt-get install -y curl   # 系統更新、安裝工具
RUN curl -LsSf https://astral.sh/uv/install.sh | sh   # 安裝 uv
COPY . /crawler                       # 把專案複製進去
WORKDIR /crawler                      # 工作目錄設在 crawler
RUN uv sync                           # 同步 Python 套件
ENV RABBITMQ_HOST=rabbitmq            # 設環境變數
CMD ["uv", "run", "celery", "-A", "crawler.worker", "worker", "--loglevel=info"]
```
> 不會寫？老師的建議：**先模仿老師的 Dockerfile 改**，或用 `docker run -it --rm ubuntu:22.04 bash` 一步步試指令，成功後整理成 SOP。

### build / push image
```bash
# build：-f 指定 Dockerfile、-t 取名(帳號/名稱:版本)、結尾的 . 代表用當前目錄
docker build -f Dockerfile -t <你的帳號>/tibame_crawler:0.0.1 .
docker images                                  # 確認建立成功
docker push <你的帳號>/tibame_crawler:0.0.1     # 上傳到 Docker Hub（需登入）
```
> 把 `linsamtw`（老師帳號）換成**你自己的 Docker Hub 帳號**。

## 五、Docker network：讓不同容器互相連線（09/14 重點）

**問題**：worker 容器連 RabbitMQ 時報錯 `Connection refused amqp://...@127.0.0.1:5672`。
**原因**：每個容器是**獨立環境**，容器裡的 `127.0.0.1` 指的是「它自己」，不是 RabbitMQ 那個容器。
**解法**：讓它們在**同一個 docker network（內網）**，並用**服務名稱**當 host 互連。

```bash
# 1) 建立共用內網
docker network create my_network
docker network ls                       # 查看內網清單

# 2) 在各 yml 裡把 networks 設為同一個、external: true
#    並把程式連線的 host 從 127.0.0.1 改成「服務名稱」，例如 rabbitmq
# 3) 重新啟動
docker compose -f rabbitmq-network.yml up -d
docker compose -f docker-compose-worker-network.yml up -d
docker logs crawler-crawler_twse-1      # 看 log 確認不再 refused
```
> 為什麼 Flower 一開始就連得上 RabbitMQ？因為它連的是**服務名稱**而不是 `127.0.0.1`。worker 也照做即可。改了程式要**重新 build image**（版本 +1，如 `0.0.2`）。

## 為什麼學這麼多 Docker？
業界（台積電、中華電信、永豐、17LIVE、美光…）都用 Docker 部署服務；常聽到的 **K8S** 背後也是以 Docker 為基礎。學會 Docker，「任何服務你都能成功部署」。

## 常見錯誤

- **docker 指令卡住/沒回應** → 對 Docker Desktop 做任意設定改動並 restart。
- **permission denied** → `sudo usermod -aG docker $USER` 後重開 terminal（或重開機）。
- **容器間連不上（Connection refused）** → 用同一個 network + 服務名稱當 host，不要用 `127.0.0.1`。
- **build 忘了結尾的 `.`** → 那個點代表 build context（當前目錄），不能少。
- **push 沒登入 / 用到老師帳號** → 先 `docker login`，image 名稱換成自己的帳號。
- **image 佔硬碟** → `docker rmi 名稱` 清掉不用的。

## 小練習

1. `docker run hello-world` 跑成功，並用 `docker ps -a` 找到它。
2. `docker run -it --rm ubuntu:22.04 bash` 進去，`apt-get update` 試裝一個工具，`exit` 離開。
3. 想一想：你的專題爬蟲若要打包，Dockerfile 的 `CMD` 應該啟動什麼指令？

⬅ 上一章：[11 Linux 指令與 Git 操作](11_linux_git.md) ｜ ➡ 下一章：[13 uv：Python 環境管理](13_uv_python_env.md)
