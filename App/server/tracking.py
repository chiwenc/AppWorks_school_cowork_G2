from server import conn

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