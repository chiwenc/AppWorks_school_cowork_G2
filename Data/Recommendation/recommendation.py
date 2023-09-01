import csv
import pymysql
from dotenv import load_dotenv
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime, timedelta
from numpy import dot
from numpy.linalg import norm
from math import acos, pi
import os
import numpy as np
from time import time

BATCH_SIZE = 50000
RATING_TABLE = "rating"
SIMILARITY_TABLE = "similarity_model"
VALID_COUNT_THRESHOLD = 0

load_dotenv(verbose=True)

db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")
db_database = os.environ.get("DB_DATABASE")

conn = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_database,
    cursorclass=pymysql.cursors.DictCursor,
)

# user: 39387
# item: 23033


def insert_similarity(similarities):
    cursor = conn.cursor()
    cursor.executemany(
        f"INSERT INTO {SIMILARITY_TABLE} (item1_id, item2_id, similarity) VALUES(%s, %s, %s)",
        similarities,
    )
    conn.commit()


def get_rating_data_from_file():
    csvfile = open("Clothing_Shoes_and_Jewelry_sample.csv")
    rows = csv.DictReader(csvfile)
    return rows


def get_rating_data_from_db(limit=None):
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {SIMILARITY_TABLE}")

    query = f"SELECT * FROM {RATING_TABLE} \
        WHERE user_id IN \
            ( SELECT user_id \
                FROM {RATING_TABLE} \
                GROUP BY user_id \
                HAVING COUNT(user_id) >= {VALID_COUNT_THRESHOLD} \
            )"
    if limit:
        query += f" ORDER BY user_id LIMIT {limit}"
    cursor.execute(query)
    conn.commit()
    return cursor.fetchall()


def group_by_user(all_rating_data):
    user_items = defaultdict(list)
    for rating_data in all_rating_data:
        user = rating_data["user_id"]
        item = rating_data["item_id"]
        rating = rating_data["rating"]
        user_items[user].append((item, float(rating)))
    return user_items


def normalize(user_items):
    normalized_user_items = defaultdict(list)
    for user, items in user_items.items():
        rating_sum = sum([item[1] for item in items])
        rating_count = len(items)
        rating_avg = rating_sum / rating_count
        for item in items:
            normalized_user_items[user].append((item[0], item[1] - rating_avg))
    return normalized_user_items


def group_by_item_pair(normalized_user_items):
    item_pair_ratings = defaultdict(list)
    for user, items in normalized_user_items.items():
        for item_rating1 in items:
            for item_rating2 in items:
                if item_rating1[0] != item_rating2[0]:
                    item_pair_ratings[(item_rating1[0], item_rating2[0])].append(
                        (item_rating1[1], item_rating2[1])
                    )
    return item_pair_ratings


def calculate_similarity(item_pair_ratings):
    item_pair_similarities = []
    for item_pair, rating_pairs in item_pair_ratings.items():
        if len(rating_pairs) < 2:
            continue
        v1 = []
        v2 = []
        for rating_pair in rating_pairs:
            v1.append(rating_pair[0])
            v2.append(rating_pair[1])
        denominator = (sum([x * x for x in v1]) ** 0.5) * (
            sum([x * x for x in v2]) ** 0.5
        )
        if denominator > 0:
            cos_sim = round(sum([x * y for x, y in zip(v1, v2)]) / denominator, 4)
            similarity = round(1 - (acos(cos_sim) / pi), 4)
            item_pair_similarities.append(
                (item_pair[0], item_pair[1], float(similarity))
            )
    return item_pair_similarities


def batch_insert(item_pair_similarities, batch_size):
    similarity_batch = np.array_split(
        np.array(item_pair_similarities, dtype="object"),
        len(item_pair_similarities) // batch_size,
    )
    for similarities in similarity_batch:
        similarities = [tuple(s) for s in similarities]
        insert_similarity(similarities)


def main():
    start_time = time()

    all_rating_data = get_rating_data_from_db()
    user_items = group_by_user(all_rating_data)
    normalized_user_items = normalize(user_items)
    item_pair_ratings = group_by_item_pair(normalized_user_items)
    item_pair_similarities = calculate_similarity(item_pair_ratings)
    batch_insert(item_pair_similarities, BATCH_SIZE)

    print("Spend Time:", time() - start_time)


if __name__ == "__main__":
    main()
