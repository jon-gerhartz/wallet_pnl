from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv('DB_NAME')

# ========== DB INIT ==========
db_exists = f"""
SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'
"""

create_db = f"""
CREATE DATABASE {DB_NAME}
"""

create_schemas = """
CREATE SCHEMA IF NOT EXISTS STG;
CREATE SCHEMA IF NOT EXISTS SRC;
"""

create_src_price_history = """
CREATE TABLE IF NOT EXISTS SRC.PRICE_HISTORY (
timestamp TIMESTAMP WITHOUT TIME ZONE,
asset TEXT,
price NUMERIC,
job_start_ts TIMESTAMP WITHOUT TIME ZONE,
UNIQUE(timestamp, asset)
)
"""

create_src_elt_log = """
CREATE TABLE IF NOT EXISTS SRC.ELT_LOG (
job_start_ts TIMESTAMP WITHOUT TIME ZONE,
status TEXT,
error CHARACTER VARYING
)
"""

# ========== ELT QUERIES ==========
create_stg_price_history = """
CREATE TABLE IF NOT EXISTS STG.PRICE_HISTORY (
unix_time BIGINT,
asset TEXT,
price NUMERIC
)
"""

drop_stg_price_history = """
DROP TABLE IF EXISTS STG.PRICE_HISTORY
"""

load_stg_price_history = """
INSERT INTO STG.PRICE_HISTORY (unix_time, price, asset)
VALUES (:unix_time, :price, :asset)
"""

load_src_price_history = """
INSERT INTO SRC.PRICE_HISTORY (timestamp, asset, price, job_start_ts)
SELECT
    DISTINCT TO_CHAR(TO_TIMESTAMP(unix_time/1000), 'YYYY-MM-DD HH24:MI')::timestamp as ts
	, asset
    , price
    , '{job_start_ts}'::timestamp
FROM stg.price_history
ON CONFLICT (timestamp, asset)
DO UPDATE SET job_start_ts = '{job_start_ts}'::timestamp
"""

insert_elt_log = """
INSERT INTO SRC.ELT_LOG (job_start_ts, status, error)
VALUES
    (:job_start_ts, :status, :error)
"""

# ========== API Queries ==========
get_src_prices = """
with max_ts as (
SELECT
	MAX(job_start_ts) as ts
FROM SRC.ELT_LOG)
SELECT
    date_trunc('hour', ph.timestamp) as hourly_ts 
    , ph.asset as token_id
    , ph.price
    , ph.job_start_ts
FROM SRC.PRICE_HISTORY ph
JOIN max_ts on max_ts.ts = ph.job_start_ts
WHERE ph.asset = '{asset}';
"""
