import csv
import pymysql
import pymysql.cursors
from urllib.parse import unquote
from collections import defaultdict
from datetime import datetime, timedelta
import random
from numpy import dot
from numpy.linalg import norm
from math import acos, pi

random.seed(datetime.utcnow())

conn = pymysql.connect(
    host = 'localhost',
    user = 'arthurlin',
    password = '1234',
    database = 'stylish_backend',
    cursorclass=pymysql.cursors.DictCursor
)

# user: 39387
# item: 23033

user_items = defaultdict(set) # {user1_index: [item1_index, item2_index, ...]}
item_users = defaultdict(set) # {item1_index: [user1_index, user2_index, ...]}
user_item_rating = {} # {(user_id, item_id): rating}
users_set = set() # {user1, user2, ...}
items_set = set() # {item1, item2, ...}
user_mapping = {} # {1: A2GRC67Y818A5B}
item_mapping = {} # {1: B00008695M}
user_inverse_mapping = {} # {A2GRC67Y818A5B: 1}
item_inverse_mapping = {} # {B00008695M: 1}

def get_rating_data(limit):
    valid_count_threshold = 7
    cursor = conn.cursor()
    query = f"SELECT * FROM rating \
        WHERE user_id IN \
            ( SELECT user_id \
                FROM rating \
                GROUP BY user_id \
                HAVING COUNT(user_id) >= {valid_count_threshold} \
            )"
    if (limit):
        query += f" ORDER BY user_id LIMIT {limit}"
    cursor.execute(query)
    conn.commit()
    return cursor.fetchall()

def insert_similarity(similarities):
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO similarity_model (item1_id, item2_id, similarity) VALUES(%s, %s, %s)",
        similarities
    )
    conn.commit()

all_rating_data = get_rating_data(None)

for row in all_rating_data:
    user_id = row["user_id"]
    users_set.add(user_id)
    item_id = row["item_id"]
    items_set.add(item_id)

index = 0
for user_id in users_set:
    user_mapping[user_id] = index
    user_inverse_mapping[index] = user_id
    index += 1

index = 0
for item_id in items_set:
    item_mapping[item_id] = index
    item_inverse_mapping[index] = item_id
    index += 1

for row in all_rating_data:
    user_id = row["user_id"]
    user_index = user_mapping[user_id]
    item_id = row["item_id"]
    item_index = item_mapping[item_id]

    user_items[user_index].add(item_index)
    item_users[item_index].add(user_index)
    user_item_rating[(user_index, item_index)] = row["rating"]

# normalize
for user_index in range(len(users_set)):
    # print("=============")
    rating_sum = sum([user_item_rating[(user_index, item_index)] for item_index in user_items[user_index]])
    # print(user_index)
    rating_count = len(user_items[user_index])
    rating_avg = round(rating_sum / rating_count, 3)
    # print('rating_sum:', rating_sum)
    # print('rating_count', rating_count)
    # print("rating_avg:", rating_avg)
    for item_index in user_items[user_index]:
        user_item_rating[(user_index, item_index)] = rating_avg

count = 0
batch_size = 10000
similarities = []

for item_index in range(len(items_set)):
    rating_users = list(item_users[item_index])
    vector = [user_item_rating[(user_index, item_index)] for user_index in rating_users]

    compare_items = set()
    for user_index in item_users[item_index]:
        for compare_item_index in user_items[user_index]:
            if compare_item_index != item_index:
                compare_items.add(compare_item_index)

    for compare_item_index in compare_items:
        count += 1
        compare_vector = [
          user_item_rating.get((user_index, compare_item_index)) or 0
          for user_index in rating_users
        ]
        cos_sim = round(dot(vector, compare_vector)/(norm(vector) * norm(compare_vector)), 3)
        similarity = round(1 - (acos(cos_sim) / pi), 4)
        # if (count<10):
        #     print("compare_vector:", compare_vector, similarity)
    
        similarities.append((
            item_inverse_mapping[item_index],
            item_inverse_mapping[compare_item_index],
            similarity
        ))
    if (count >= batch_size):
        insert_similarity(similarities)
        count = 0
        similarities = []
