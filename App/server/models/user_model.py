from server import conn

def get_user(email):
    select_user_sql = """
        SELECT *
        FROM user
        WHERE email = %s
    """

    cursor = conn.cursor()
    cursor.execute(select_user_sql, [email])
    user = cursor.fetchone()
    conn.commit()
    return user

def create_user(provider, email, password, name, access_token, access_expire):
    create_user_sql = """
        INSERT INTO user (provider, email, password, name, access_token, access_expired)
        VALUES(%s, %s, %s, %s, %s, %s)
    """

    cursor = conn.cursor()
    cursor.execute(create_user_sql, [provider, email, password, name, access_token, access_expire])
    conn.commit()
    return cursor.lastrowid

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