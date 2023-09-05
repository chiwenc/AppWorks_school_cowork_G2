import pymysql
from config import Config
import random

mysql_config = Config()


def get_product_info(category):
    connection = pymysql.connect(**mysql_config.db_config)
    with connection.cursor() as cursor:
        cursor.execute('SELECT id, category FROM product WHERE category = %s', (category,))
        all_items = cursor.fetchall()
        cursor.close()
    return all_items


results = get_product_info(category="men")
for i in results:
    fake_user_id = random.randrange(0, 100, 1)
