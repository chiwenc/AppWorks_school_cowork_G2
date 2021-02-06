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

cursor = conn.cursor()
cursor.execute(
    "SELECT * FROM rating LIMIT 10000"
)
all_rating_data = cursor.fetchall()
conn.commit()

valid_user_items = defaultdict(set)
for row in all_rating_data:
    user_id = row["user_id"]
    users_set.add(user_id)
    item_id = row["item_id"]
    items_set.add(item_id)
    valid_user_items[user_id].add(item_id)

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

# Only users who rated more then 3 different items are valid users
valid_users_set = set()
valid_threshold = 3
for user_id in users_set:
    if (len(valid_user_items[user_id]) >= valid_threshold):
        valid_users_set.add(user_mapping[user_id])

# print("valid_users_set:", valid_users_set)

for row in all_rating_data:
    user_id = row["user_id"]
    user_index = user_mapping[user_id]
    item_id = row["item_id"]
    item_index = item_mapping[item_id]

    if (user_index in valid_users_set): 
        user_items[user_index].add(item_index)
        item_users[item_index].add(user_index)
        user_item_rating[(user_index, item_index)] = row["rating"]

# normalize
for user_index in valid_users_set:
    # print("=============")
    rating_sum = sum([user_item_rating[(user_index, item_index)] for item_index in user_items[user_index]])
    # print(user_index)
    # print(user_items[user_index])
    rating_count = len(user_items[user_index])
    rating_avg = rating_sum / rating_count
    # print('rating_sum:', rating_sum)
    # print('rating_count', rating_count)
    # print("rating_avg:", rating_avg)
    for item_index in user_items[user_index]:
        user_item_rating[(user_index, item_index)] -= rating_avg

zz = 0
for item_index in range(len(items_set)):
    # if (zz<10):
    rating_users = list(item_users[item_index])
    if not rating_users: # item haven't rated by any valid user yet.
        continue
    # print("--- item_index:", item_index)
    vector = [user_item_rating[(user_index, item_index)] for user_index in rating_users]
    if (zz < 10):
        print('------------')
        print("vector:", vector)
    compare_items = set()
    for user_index in item_users[item_index]:
        for compare_item_index in user_items[user_index]:
            if compare_item_index != item_index:
                compare_items.add(compare_item_index)
    # if (zz < 10):
    #     print(compare_items)
    # print(vector)
    for compare_item_index in compare_items:
        # print("compare item:", compare_item_index)
        compare_vector = [0 for i in rating_users]
        for i in range(len(rating_users)):
            compare_vector[i] = user_item_rating.get((rating_users[i], compare_item_index))
            if not compare_vector[i]:
                compare_vector[i] = 0
        
        if (zz<10):
            print("compare_vector:", compare_vector)

        # XXX: calculate cosine similarity between vector & compare_vector
        # XXX: store result in DB

    zz += 1

# print(user_items)