# 26 · Docker Swarm 介紹

> 對應課程：10/05（Docker Swarm 1/2）

## 重點摘要

當你部署的服務超過 10 個（RabbitMQ、MySQL、worker、API、Redash…），而且分散在很多台 VM，要**有效管理、查看 log** 很痛苦。**Docker Swarm** 就是來解決這個的——可視為**輕量版的 K8s**，用一台 manager 就能控制多台機器。

## 核心觀念

### 1. Compose vs Swarm
| | 管什麼 | 範圍 |
|--|--------|------|
| **Docker** | 一個 container | 單一服務 |
| **Docker Compose** | 多個 container | 一台機器 |
| **Docker Swarm** | 多個 compose（stack）| **多台 VM** |

- Swarm 能**管理多台 VM**：worker 分散在 10 台雲端 VM（避免被 ban IP）；程式改動後，**在 manager 一台就能對所有 Node 換 image 版本、部署新服務、查看 log**，不用手動登入每台。

### 2. Swarm vs K8s（Kubernetes）
- 差別在**複雜度**：K8s 較複雜、適合大型架構/大公司；**Swarm 較簡單、適合小型專案/團隊**。
- 初學者先從 Swarm 開始；資料工程師技能樹之一。

### 3. 角色：Manager / Node(Worker)
- **Manager 主管**：發號指令（換 image、查 log、部署）。
- **Node / Worker 工人**：負責做事（跑 container）。
- 你只需當 manager 發指令，工人負責完成。

## 一、建立 Swarm

```bash
# 先清掉舊的 compose 容器（要改用新架構）
docker rm -f $(docker ps -a -q)

docker swarm init                    # 初始化 Swarm（這台變 manager）
docker swarm join-token worker       # 忘記加入指令時，查 worker 加入的 token
```

## 二、Portainer：Swarm 的 Web 管理介面

Portainer = 一站式管理所有 Services / Container（MySQL、RabbitMQ、Flower、Crawler…）的**網頁介面**。
```bash
docker pull portainer/portainer-ce:2.0.1
docker pull portainer/agent
docker stack deploy -c portainer.yml por     # 部署 Portainer（約 1 分鐘）
# 開 http://127.0.0.1:9000/ → 設 admin / 密碼
```
- **Portainer**：manager 的管理介面，可控制多個 Node、查看 log（不用再背指令/port）。
- **Agent**：自動部署在每個 Manager/Worker 上，把 manager 的指令傳給 worker（靠掛載 `/var/run/docker.sock` 控制該機的 Docker）。

### `docker stack deploy -c xxx.yml 名稱` 是什麼？
- **stack**：一個 compose 裡的多個 service，合稱一個 stack。
- `deploy`：部署；`-c xxx.yml`：用哪個 yml；最後是 stack 名稱。

## 三、Swarm 的 network 與 volume（和 Compose 的差異）

```bash
# Compose 章節（單機）
docker network create my_network

# Swarm 章節（跨機）
docker network create --scope=swarm --driver=overlay my_swarm_network
```
- `--scope=swarm`：讓 Swarm 所有 Node 都能用。
- `--driver=overlay`：**overlay 網路**，雖是內網但**允許跨 VM 溝通**。
- `--attachable`：允許非 swarm 的 container 也連進來（部署 rabbitmq/flower 時用到）。
- volume：`docker volume create mysql`（存 MySQL 資料，持久化）。

## 四、用 Swarm 部署服務（stack）

```bash
docker stack deploy --with-registry-auth -c mysql.yml mysql
docker stack deploy --with-registry-auth -c rabbitmq.yml rabbitmq
```
- `--with-registry-auth`：帶 registry 認證（讓 Node 能 pull 你 Docker Hub 的私有 image）。
- 部署後到 **Portainer** 就看得到 services、可直接看每個 container 的 **log**（Container → Logs）。
- yml 幾乎**沿用 Compose 的設定**，只多加 `deploy`/network 調整——前面學的沒白費。

### MySQL 資料不見？用回舊 volume
```bash
docker volume ls          # 找到之前的 volume（例如 crawler_mysql）
# 在 mysql.yml 改用那個 volume → 移除 stack 重建 → table 復原
```

## 五、回到 Compose

```bash
docker swarm leave --force     # 離開 swarm
docker ps -a                   # 容器已全數關閉
```

## 常見錯誤

- **忘了用 overlay network**：Swarm 跨機要 `--driver=overlay --scope=swarm`，不是 `my_network`。
- **pull 不到私有 image**：stack deploy 要加 `--with-registry-auth`。
- **port 被占用**：Portainer 用 9000；若 phpMyAdmin 原本 8000 被占，改 8080。
- **Mac 無法部署 portainer agent**：agent 靠 `docker.sock`，Mac 環境不支援。

## 小練習

1. `docker swarm init` 後部署 Portainer，打開 `http://127.0.0.1:9000` 看介面。
2. 用 `docker stack deploy` 部署一個 mysql stack，到 Portainer 看它的 log。
3. 說出 Compose 與 Swarm 的 network 建立指令差在哪。

⬅ 上一章：[25 資料視覺化：Redash](25_redash_visualization.md) ｜ ➡ 下一章：[27 Docker Swarm 實戰](27_docker_swarm_practice.md)
