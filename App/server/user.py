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