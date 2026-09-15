-- 被動式 ETF 資料庫結構（對應課程 15~20：DDL / DML / PyMySQL）
-- 用法：先在 MySQL 建一個資料庫，再執行本檔建立三張表。
--   CREATE DATABASE IF NOT EXISTS etf DEFAULT CHARACTER SET utf8mb4;
--   USE etf;
--   SOURCE schema.sql;

-- 1) 每日股價（含還原收盤 adj_close）
CREATE TABLE IF NOT EXISTS etf_price (
    symbol      VARCHAR(16)   NOT NULL,           -- ETF 代號，如 0050.TW
    trade_date  DATE          NOT NULL,           -- 交易日
    open        DECIMAL(12,4),
    high        DECIMAL(12,4),
    low         DECIMAL(12,4),
    close       DECIMAL(12,4),                    -- 收盤（Yahoo 通常已還原分割）
    adj_close   DECIMAL(12,4),                    -- 還原收盤（分割+除權息）→ 算長期報酬用
    volume      BIGINT,
    PRIMARY KEY (symbol, trade_date)              -- 同一檔同一天只會有一筆（避免重複）
);
-- 常用查詢：某檔的時間序列 → 對 symbol 建索引（course 19）
CREATE INDEX IDX_price_symbol ON etf_price (symbol);

-- 2) 除權息紀錄
CREATE TABLE IF NOT EXISTS etf_dividend (
    symbol   VARCHAR(16)   NOT NULL,
    ex_date  DATE          NOT NULL,              -- 除息日
    amount   DECIMAL(12,6) NOT NULL,              -- 每股配發金額
    PRIMARY KEY (symbol, ex_date)
);

-- 3) 分割紀錄（台股 ETF 常已還原，可能沒有資料；美股較常見）
CREATE TABLE IF NOT EXISTS etf_split (
    symbol       VARCHAR(16)  NOT NULL,
    split_date   DATE         NOT NULL,
    numerator    DECIMAL(12,4),                   -- 分割比例分子
    denominator  DECIMAL(12,4),                   -- 分割比例分母
    ratio        VARCHAR(16),                     -- 如 "4:1"
    PRIMARY KEY (symbol, split_date)
);
