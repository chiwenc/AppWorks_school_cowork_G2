import re
import pymysql  
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
import random
import time
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)
db_host = os.environ.get('DB_SOURCE_HOST')
db_user = os.environ.get('DB_SOURCE_USERNAME')
db_password = os.environ.get('DB_SOURCE_PASSWORD')
db_database = os.environ.get('DB_SOURCE_DATABASE')

conn = pymysql.connect(
    host = db_host,
    user = db_user,
    password = db_password,
    database = db_database,
    cursorclass = pymysql.cursors.DictCursor
)

all_events = defaultdict(list)

def parse(url):
    change = random.randint(0, 100)
    if (change < 50):
        parts = re.search(r"(.*)cid=([\w-]*)&(.*)", url)
        cid = parts.group(2)
        N = 5
        last_N_digit = ""
        for i in range(N):
            last_N_digit += chr(random.randint(0, 25) + 97)
        new_cid = cid[0:-N] + last_N_digit
        return parts.group(1) + "cid=" + new_cid + "&" + parts.group(3)
    else:
        return url

def generate():
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) as count FROM tracking_raw')
    count = cursor.fetchone()['count']

    limit = random.randint(5, 100)
    offset = random.randint(0, count - limit) 

    cursor.execute(f'SELECT request_url FROM tracking_raw LIMIT {offset}, {limit}')
    rows = cursor.fetchall()
    for row in rows:
        print('write:', row["request_url"])
        new_request_url = parse(row["request_url"])
        cursor.execute(
            f"INSERT INTO tracking_raw_realtime (request_url) \
              VALUES('{new_request_url}')"
        )
        conn.commit()
        time.sleep(random.randint(1,5))

def main():
    for i in range(1,100):
        generate()

main()