import csv
import pymysql
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime, timedelta
import random
random.seed(datetime.utcnow())

conn = pymysql.connect(
    host = 'localhost',
    user = 'arthurlin',
    password = '1234',
    database = 'stylish_backend',
    cursorclass=pymysql.cursors.DictCursor
)
import json 

def insert_rating(ratings):
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO rating (user_id, item_id, rating, time) VALUES(%s, %s, %s, %s)",
        ratings
    )
    conn.commit()

with open('/Users/arthurlin/Downloads/reviews_Clothing_Shoes_and_Jewelry_5.json') as f:
    count = 0
    batch_size = 10000
    ratings = []
    for line in f:
        count += 1
        data = json.loads(line)
        ratings.append((
            data['reviewerID'],
            data['asin'],
            data['overall'],
            datetime.fromtimestamp(data['unixReviewTime']), 
        ))
        if (count == batch_size):
            count = 0
            insert_rating(ratings)
            ratings = []
    if (count > 0):
        insert_rating(ratings)
        ratings = []

# user: 39387
# item: 23033

