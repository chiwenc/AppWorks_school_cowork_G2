import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup

conn = pymysql.connect(
    host = 'localhost',
    user = 'arthurlin',
    password = '1234',
    database = 'stylish_data_engineering',
    cursorclass=pymysql.cursors.DictCursor
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Accept-Language': 'en-US'
}
cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

def get_items():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT(item1_id) AS item_id FROM similarity_model LIMIT 6"
    )
    conn.commit()
    return cursor.fetchall()

def get_similar_items(item_id):
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT item2_id AS item_id FROM similarity_model WHERE item1_id = '{item_id}' ORDER BY similarity DESC LIMIT 6"
    )
    conn.commit()
    return cursor.fetchall()

def insert_product(item_id, title, image):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO amazon_product (item_id, title, image) VALUES(%s, %s, %s)",
        (item_id, title, image)
    )
    conn.commit()

def fetch_data(item_id):
    url = f"https://www.amazon.com/dp/{item_id}"
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text 
        # print(web_content)
        soup = BeautifulSoup(web_content, 'html.parser')
        # print(soup)
        title = soup.find('span', id="productTitle").text.strip()
        image = soup.find('div', id="main-image-container").find('img').get('src').strip()
        # print(title, image)
        insert_product(item_id, title, image)
        print("OK")
    except Exception as e:
        print("ERROR:", url, e)

items = get_items()
for item in items:
    item_id = item['item_id']
    fetch_data(item_id)
    similar_items = get_similar_items(item_id)
    for similar_item in similar_items:
        fetch_data(similar_item['item_id']) 


# import time
# import threading
# import queue

# # Worker 類別，負責處理資料
# class Worker(threading.Thread):
#   def __init__(self, queue, num):
#     threading.Thread.__init__(self)
#     self.queue = queue
#     self.num = num
#     self.conn = pymysql.connect(
#         host = 'localhost',
#         user = 'arthurlin',
#         password = '1234',
#         database = 'stylish_data_engineering',
#         cursorclass=pymysql.cursors.DictCursor
#     )
#   def run(self):
#     while self.queue.qsize() > 0:
#       # 取得新的資料
#       item_id = self.queue.get()

#       # 處理資料
#       print(f"Worker: {self.num}, Item: {item_id}")
#       fetch_data(self.conn, item_id)
#     #   time.sleep(1)

# # 建立佇列
# my_queue = queue.Queue()

# items = get_items()
# for item in items:
#     my_queue.put(item['item_id'])

# print(my_queue)

# workers = []
# for i in range(1):
#     worker = Worker(my_queue, i)
#     workers.append(worker)

# # 讓 Worker 開始處理資料
# for worker in workers:
#     worker.start()

# # 等待所有 Worker 結束
# for worker in workers:
#     worker.join()


# print("Done.")