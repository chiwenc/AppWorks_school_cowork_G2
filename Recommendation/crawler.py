import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup
import threading
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

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

HEADERS = {
    'authority': 'scrapeme.live',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

cookies = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

def get_items():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT(item1_id) AS item_id FROM similarity_model LIMIT 5000, 12"
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

def insert_product(item_id, title, source, image):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO product (id, title, source, image_base64) VALUES(%s, %s, %s, %s)",
        (item_id, title, source, image)
    )
    conn.commit()

def fetch_data(item_id):
    url = f"https://www.amazon.com/dp/{item_id}"
    print("URL:", url)
    try:
        r = requests.get(url, headers=HEADERS, cookies=cookies)
        web_content = r.text 
        soup = BeautifulSoup(web_content, 'html.parser')
        title = soup.find('span', id="productTitle").text.strip()
        image = soup.find('div', id="main-image-container").find('img').get('src').strip()
        insert_product(item_id, title, 'amazon', image)
        print("OK")
    except Exception as e:
        print("ERROR:", url, e)

items = get_items()
for item in items:
    item_id = item['item_id']
    t = threading.Thread(target = fetch_data, args = (item_id,))
    t.start()
    sleep(1)
    fetch_data(item_id)
    similar_items = get_similar_items(item_id)
    for similar_item in similar_items:
        t = threading.Thread(target = fetch_data, args = (similar_item['item_id'],))
        t.start()
        sleep(1)
