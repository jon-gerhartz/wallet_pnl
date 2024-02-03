from dotenv import load_dotenv
from queries import db_exists, create_db, create_schemas, create_src_price_history, create_src_elt_log
import os
import pg8000

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_PW = os.getenv("DB_PW")
INIT_DB_NAME = os.getenv("INIT_DB_NAME")


def create_conn(DB_NAME):
    conn = pg8000.connect(
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        password=DB_PW
    )
    return conn


init_conn = create_conn(INIT_DB_NAME)
init_conn.autocommit = True

with init_conn.cursor() as cur:
    cur.execute(db_exists)
    exists = cur.fetchone()

    if not exists:
        cur.execute(create_db)
        init_conn.commit()
    cur.close()
    init_conn.close()

conn = create_conn(DB_NAME)
run_list = [create_schemas, create_src_price_history, create_src_elt_log]

with conn.cursor() as cur:
    try:
        for i in run_list:
            cur.execute(i)
        conn.commit()
        message = 'successfully commited migrations'
    except Exception as e:
        message = e
    print(message)
