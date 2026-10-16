# 27 · Docker Swarm 實戰（分散式爬蟲 / API / Redash）

> 對應課程：10/08~10/12（Docker Swarm 2/2）

## 重點摘要

用 [Docker Swarm](26_docker_swarm_intro.md) 把**分散式爬蟲、API、Redash** 全部重新部署，並學會：用 **Node Labels** 指定「哪個服務跑在哪台機器」、用 **Task.Slot / replicas** 一鍵擴展工人、以及**分散式 API 自動分流**。

> 重點心法：Swarm 這兩堂課**幾乎沒寫程式**——分散式架構更多是 **Docker 層面的設計**，連 `docker-compose.yml` 都是沿用之前的。

## 一、Node Labels：讓不同 Node 跑不同任務

為什麼要分？
- 不同爬蟲放不同 VM（twse 一台、tpex 一台）→ 效率加倍、分散 IP。
- 不同硬體需求：有的任務要 GPU（機器學習）、有的只要大記憶體、selenium 比 requests 吃資源。

做法：**在 Node 設 Label，在 service 設 placement 對應 Label**。
```yaml
# docker-compose-worker-...-swarm.yml（沿用 compose，只多 deploy/placement）
services:
  crawler_twse:
    image: ${DOCKER_IMAGE_VERSION 之類}
    deploy:
      placement:
        constraints:
          - node.labels.crawler_twse == true   # 只部署到有此 label 的 Node
    networks:
      - my_attachable_network
```
在 **Portainer → Swarm → 該 Node → Node Details → Labels** 設定：
```
Node VM2 → rabbitmq=true, flower=true
Node VM3 → crawler_twse=true, crawler_tpex=true
Node VM4 → mysql=true, producer=true, scheduler=true
```
→ 不同 service 自動部署到對應 Node。

部署與發送任務：
```bash
DOCKER_IMAGE_VERSION=0.0.6 docker stack deploy --with-registry-auth \
  -c docker-compose-worker-network-version-swarm.yml crawler
# 發送任務（producer 也用 stack deploy）→ 到 MySQL 看資料進來
```

## 二、一鍵擴展工人：replicas 與 Task.Slot

想把 crawler 從 1 台擴成多個工人 → 設 **replicas**（副本數），Swarm 一鍵拉起 N 個 container。

**Flower 只顯示 2 個工人的問題**：Flower 顯示的是 Celery 的 **hostname**，多個副本 hostname 相同會被合併。解法：hostname 尾綴加上 **`{{.Task.Slot}}`**（Swarm 的任務槽編號），每個副本就有不同 hostname。
```yaml
command: celery -A crawler.worker worker -n worker@{{.Task.Slot}} ...
```
→ 例如 1 個 twse + 3 個 tpex，Flower 就正確顯示 4 個工人。

**威力**：
- 老闆說爬蟲量要變 10 倍 / 更新頻率從每天變每小時（24 倍）→ 分散式架構**一天內完成**。
- 效能不再是問題，問題是 **$$$**（機器成本）。

## 三、分散式 API（自動分流）

```bash
DOCKER_IMAGE_VERSION=0.0.1 docker stack deploy --with-registry-auth \
  -c docker-compose-api-network-version-swarm.yml api
```
- 設 API 的 Node Label → 部署 → 開 `http://127.0.0.1:8888/docs` 測試。
- **Python 是單核心，單一 API 太慢** → 一鍵擴展成多個 container。
- 發 10 次 request，Swarm **自動隨機分流**到 3 個 container（例：5 / 3 / 2 筆）。
- 這是單純 Docker/Compose/Python **做不到**的：業界一定要分流，不可能只靠一隻 API。

## 四、Swarm 部署 Redash

```bash
docker stack deploy -c docker-compose-redash.yml redash
# 所有 service 設 placement: node.labels.redash == true
# 開 http://localhost:5005/
```
用法參考 [25 章 Redash](25_redash_visualization.md)。

## 重複發送任務 / 重跑（Portainer 操作）
- 想再發一次任務：進 Portainer 找到該 producer 的 Container → **Start**；或先把資料清空歸 0 再發。
- Swarm 下的 task，`Complete` 代表任務結束。

## 常見錯誤

- **service 沒設 placement / Node 沒設 Label**：服務一直 `pending`，不會啟動。
- **多副本 Flower 只顯示 1~2 個**：hostname 要加 `{{.Task.Slot}}`。
- **以為要改很多程式**：Swarm 幾乎是 yml/Docker 層面設計，沿用 Compose 的 yml。
- **忘了 `--with-registry-auth`**：Node pull 不到私有 image。

## 小練習

1. 幫兩個 service 設不同 Node Label 與 placement，觀察它們部署到不同（或同）Node。
2. 把 crawler 的 replicas 設成 3，到 Flower 確認工人數（記得 `{{.Task.Slot}}`）。
3. 想一想：你的 ETF 專題若要「同時爬很多檔、再上傳 DB」，怎麼用 Swarm 擴展工人？

⬅ 上一章：[26 Docker Swarm 介紹](26_docker_swarm_intro.md) ｜ ➡ 下一章：[28 Airflow](28_airflow.md)
