import pymysql
import os
import random

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

def get_user_behavior_by_date(date):
    select_analysis_sql = """
        SELECT *
        FROM tracking_analysis
        WHERE date = %s
    """

    cursor = conn.cursor()
    cursor.execute(select_analysis_sql, date + ' 00:00:00')
    data = cursor.fetchone()
    conn.commit()
    return data