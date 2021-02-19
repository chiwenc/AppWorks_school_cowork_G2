import re
import pymysql  
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
import random
import time
from dotenv import load_dotenv
import os
from datetime import datetime
from pymongo import MongoClient

load_dotenv(verbose=True)

mongo_host = os.environ.get('MONGO_HOST')
mongo_user = os.environ.get('MONGO_USERNAME')
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_database = os.environ.get('MONGO_DATABASE')

mysql_host = os.environ.get('MYSQL_HOST')
mysql_user = os.environ.get('MYSQL_USERNAME')
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_database = os.environ.get('MYSQL_DATABASE')

client = MongoClient(mongo_host,
    username = mongo_user,
    password = mongo_password,
    authMechanism = 'SCRAM-SHA-1')
db = client[mongo_database]
collection = db['tracking_raw_realtime']
# delete: db.tracking_raw_realtime.remove({})

conn = pymysql.connect(
    host = mysql_host,
    user = mysql_user,
    password = mysql_password,
    database = mysql_database,
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
            "INSERT INTO tracking_raw_realtime (request_url) \
              VALUES(%s)",
            (new_request_url)
        )
        conn.commit()

        data = {
            "request_url": new_request_url, 
            "created_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        x = collection.insert_one(data)
        print(x)

        time.sleep(random.randint(1,5))

def main():
    for i in range(1,100):
        generate()

main()





# print(datetime.utc_now())