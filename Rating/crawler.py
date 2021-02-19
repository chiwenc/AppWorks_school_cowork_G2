import pymysql
import pymysql.cursors
import requests
from bs4 import BeautifulSoup
import threading
from time import sleep

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
        "INSERT INTO amazon_product (id, title, image_base64) VALUES(%s, %s, %s)",
        (item_id, title, image)
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
        insert_product(item_id, title, image)
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
