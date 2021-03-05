import re
import pymysql  
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv(verbose=True)

mongo_host = os.environ.get('MONGO_HOST')
mongo_user = os.environ.get('MONGO_USERNAME')
mongo_auth = os.environ.get('MONGO_AUTH_SOURCE')
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_database = os.environ.get('MONGO_DATABASE')

mysql_host = os.environ.get('MYSQL_HOST')
mysql_user = os.environ.get('MYSQL_USERNAME')
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_database = os.environ.get('MYSQL_DATABASE')

client = MongoClient(mongo_host,
    username = mongo_user,
    password = mongo_password,
    authSource = mongo_auth,
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

def parse(row):
    start_time = row['created_at']
    data = row['request_url']
    obj = {}
    client_id = re.search(r"cid=([\w-]*)&", data)
    obj['cid'] = client_id.group(1)
    obj['start_time'] = start_time
    event_type = re.search(r"evtn=(\w*)&", data)
    obj['event'] = event_type.group(1)
    contents = re.findall(r"evtk\w*=([\w%]*)&evt\w*=([\w%]*)", data)
    for (key, value) in contents:
        obj[key] = unquote(value)
    return obj

def clean_data(last_time, current_time):
    print(last_time.strftime('%Y-%m-%d %H:%M:%S'), current_time.strftime('%Y-%m-%d %H:%M:%S'))
    rows = db.tracking_raw_realtime.find({"created_at": {"$gt": last_time.strftime('%Y-%m-%d %H:%M:%S'), "$lte": current_time.strftime('%Y-%m-%d %H:%M:%S')}})
    cursor = conn.cursor()
    for row in rows: 
        obj = parse(row)
        print(obj)
        event = obj['event']
        view_detail = obj.get('view_detail')
        item_id = obj.get('item_id')
        item_id = item_id if (item_id and item_id.isdigit()) else None
        checkout_step = obj.get('checkout_step')
        
        insert_sql = "INSERT INTO tracking_realtime (client_id, time, event_type, view_detail, item_id, checkout_step) \
              VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (obj['cid'], obj['start_time'], event, view_detail, item_id, checkout_step))
    conn.commit()

def aggregate_data(current_time):
    current_time = current_time.strftime('%Y-%m-%d 00:00:00')
    print('current_time:', current_time)

    cursor = conn.cursor()
    select_today_user_sql = "SELECT DISTINCT(client_id) FROM tracking_realtime WHERE time >= %s"
    select_before_user_sql = "SELECT DISTINCT(client_id) FROM tracking_realtime WHERE time < %s"
    select_all_user_sql = "SELECT COUNT(DISTINCT(client_id)) AS count FROM tracking_realtime"
    cursor.execute(select_today_user_sql, (current_time))
    today_users = cursor.fetchall()
    cursor.execute(select_before_user_sql, (current_time))
    before_users = cursor.fetchall()
    cursor.execute(select_all_user_sql)
    all_users = cursor.fetchall()

    all_before_users = set()
    all_user_count = int(all_users[0]['count'])
    active_user_count = 0
    new_user_count = 0
    return_user_count = 0

    for user in before_users:
        all_before_users.add(user['client_id'])

    for user in today_users:
        active_user_count += 1
        if (user['client_id'] in all_before_users):
            return_user_count += 1
        else:
            new_user_count += 1

    print('all:', all_user_count)
    print('unique:', active_user_count)
    print('new:', new_user_count)
    print('return', return_user_count)

    select_user_behavior_sql = '''
        SELECT 
            SUM(CASE WHEN event_type = 'view' then 1 ELSE 0 END) as "view_count",
            SUM(CASE WHEN event_type = 'view_item' then 1 ELSE 0 END) as "view_item_count",
            SUM(CASE WHEN event_type = 'add_to_cart' then 1 ELSE 0 END) as "add_to_cart_count",
            SUM(CASE WHEN (event_type = 'checkout_progress' AND checkout_step = '1') then 1 ELSE 0 END) as "checkout_count"
        FROM tracking_realtime
        WHERE time >= %s
    '''

    cursor.execute(select_user_behavior_sql, (current_time))
    user_behavior = cursor.fetchone()
    print(user_behavior)

    update_analysis_sql = '''
        INSERT INTO tracking_analysis (`date`, all_user_count, active_user_count, new_user_count, return_user_count, view_count, view_item_count, add_to_cart_count, checkout_count) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        all_user_count = %s,
        active_user_count = %s,
        new_user_count = %s,
        return_user_count = %s,
        view_count = %s,
        view_item_count = %s,
        add_to_cart_count = %s,
        checkout_count = %s
    '''

    cursor.execute(update_analysis_sql, (
        current_time,
        all_user_count, active_user_count, new_user_count, return_user_count,
        user_behavior['view_count'], user_behavior['view_item_count'], user_behavior['add_to_cart_count'], user_behavior['checkout_count'],
        all_user_count, active_user_count, new_user_count, return_user_count,
        user_behavior['view_count'], user_behavior['view_item_count'], user_behavior['add_to_cart_count'], user_behavior['checkout_count']
    ))
    conn.commit()

def main():
    last_time = datetime.utcnow() - timedelta(seconds=10)
    for i in range(1,100):
        current_time = datetime.utcnow() - timedelta(seconds=10)
        clean_data(last_time, current_time)
        aggregate_data(current_time)
        last_time = current_time
        time.sleep(5)

main()