import os, pymysql
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
cursor = conn.cursor()

def get_fav(user_id):
    sql_check_fav = "SELECT distinct(fav_product_id) FROM favorite WHERE user_id = %s"
    cursor.execute(sql_check_fav, (user_id,))
    results = cursor.fetchall()
    fav_product_id_list = [results[i]["fav_product_id"] for i in range(len(results))]
    return fav_product_id_list

def insert_fav(user_id, fav_product_id):
    sql_insert_fav = "INSERT INTO favorite (user_id, fav_product_id) VALUEs (%s,%s)"
    cursor.execute(sql_insert_fav, (user_id, fav_product_id))
    conn.commit()

def delete_fav(user_id, fav_product_id):
    sql_delete_fav = "DELETE FROM favorite WHERE user_id = %s AND fav_product_id = %s"
    cursor.execute(sql_delete_fav, (user_id, fav_product_id))
    conn.commit()

# insert_fav(50,123)
delete_fav(50,123)
print(get_fav(50))
