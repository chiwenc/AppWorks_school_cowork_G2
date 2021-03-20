import boto3
import csv
from dotenv import load_dotenv
import pymysql
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime, timedelta
import random
import json
import os

load_dotenv(verbose=True)
random.seed(datetime.utcnow())

db_host = os.environ.get('DB_HOST')
db_user = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
db_database = os.environ.get('DB_DATABASE')

conn = pymysql.connect(
    host = db_host,
    user = db_user,
    password = db_password,
    database = db_database,
    cursorclass = pymysql.cursors.DictCursor
)

def insert_rating(ratings):
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO rating (user_id, item_id, rating, time) VALUES(%s, %s, %s, %s)",
        ratings
    )
    conn.commit()

def parse_data(data):
    count = 0
    batch_size = 10000
    ratings = []
    for row in data:
        count += 1
        data = json.loads(row)
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

# read from file
def read_from_file():
    with open('sample_data.json') as data:
        parse_data(data)

# read from S3
def read_from_s3():
    s3 = boto3.resource('s3')
    # user count: 39387
    # item count: 23033
    content_object = s3.Object('stylish-data-engineering', 'data.json')
    data = content_object.get()['Body'].read().decode('utf-8').splitlines()
    parse_data(data)

def main():
    read_from_file()
    # read_from_s3()

main()