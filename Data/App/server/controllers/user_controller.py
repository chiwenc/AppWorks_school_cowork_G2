import bcrypt
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server import app
from ..models.user_model import get_user, create_user
from ..models.tracking_model import get_user_behavior_by_date
from ..utils.util import dir_last_updated
from pytz import timezone
import json
import pymysql
import datetime
import uuid
from config import Config

mysql_config = Config()

TOKEN_EXPIRE = app.config['TOKEN_EXPIRE']


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))


@app.route('/signin', methods=['GET'])
def signin_page():
    return render_template('signin.html', last_updated=dir_last_updated('server/static'))


@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html', last_updated=dir_last_updated('server/static'))


@app.route('/profile', methods=['GET'])
def profile_page():
    return render_template('profile.html', last_updated=dir_last_updated('server/static'))


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', last_updated=dir_last_updated('server/static'))


@app.route('/api/1.0/signin', methods=['POST'])
def api_signin():
    form = request.get_data()
    form = json.loads(form)
    email = form['email']
    password = form['password']

    user = get_user(email)
    if not user:
        return jsonify({"error": "Bad username"}), 401

    if not check_password(password, user["password"]):
        return jsonify({"error": "Bad password"}), 401

    access_token = create_access_token(identity=user["name"])
    # conn = pymysql.connect(**mysql_config.db_config)
    # with conn.cursor() as cursor:
    #     cursor.execute('UPDATE user SET access_token = %s WHERE email = %s', (access_token, email))
    #     conn.commit()
    return {
        "data": {
            "access_token": access_token,
            "access_expired": TOKEN_EXPIRE,
            "user": {
                "id": user["id"],
                "provider": 'native',
                "name": user["name"],
                "email": email,
                "picture": ""
            }
        }
    }


@app.route('/api/1.0/signup', methods=['POST'])
def api_signup():
    form = request.get_data()
    form = json.loads(form)
    name = form['name']
    email = form['email']
    password = form['password']
    encrypted_password = get_hashed_password(password)
    user = get_user(email)
    if user:
        return jsonify({"error": "User already existed"}), 401
    access_token = create_access_token(identity=name)
    user_id = create_user({
        "provider": 'native',
        "email": email,
        "password": encrypted_password,
        "name": name,
        "picture": None,
        "access_token": access_token,
        "access_expired": TOKEN_EXPIRE
    })

    return {
        "data": {
            "access_token": access_token,
            "access_expired": TOKEN_EXPIRE,
            "user": {
                "id": user_id,
                "provider": 'native',
                "name": name,
                "email": email,
                "picture": ""
            }
        }
    }


@app.route('/api/1.0/profile', methods=['GET'])
@jwt_required
def api_get_user_profile():
    current_user = get_jwt_identity()
    # msg for expired token: {"msg": "Token has expired"}
    return f"Welcome! {current_user}"

@app.route('/api/1.0/user/behavior/<date>')
def api_get_user_behavior(date):
    data = get_user_behavior_by_date(date)
    if (data):
        return {
            "behavior_count": [data['view_count'], data['view_item_count'], data['add_to_cart_count'], data['checkout_count']],
            "user_count": [data['all_user_count'], data['active_user_count'], data['new_user_count'], data['return_user_count']]
        }
    else:
        return {
            "behavior_count": [0]*4,
            "user_count": [0]*4
        }

@app.route('/api/1.0/user/tracking', methods=['GET'] )
def tracking():
    uuid = request.values.get("uuid")
    event_type = request.values.get("event_type")
    event_detail = request.values.get("event_detail")
    source = request.values.get("source")
    
    current_time = datetime.datetime.now()
    utc8_time = current_time.astimezone(timezone('Asia/Taipei'))
    
    conn = pymysql.connect(**mysql_config.db_config)    
    with conn.cursor() as cursor:
        sql_insert_tracking = """
            INSERT INTO tracking (uuid, event_type, event_detail, source, time)
            VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_insert_tracking, (uuid, event_type, event_detail, source, utc8_time))
        conn.commit()
    return "Successfully capture user behavior.", 200


# @app.route('/api/1.0/ab_test/click/<source>')
# def click(source):
#     time = datetime.datetime.now()
#     product_id = request.values.get("product_id")
#     uuid = request.values.get("uuid")
    
#     conn = pymysql.connect(**mysql_config.db_config)    
#     with conn.cursor() as cursor:
#         sql_insert_click = """
#             INSERT INTO ab_testing_click (time, uuid, product_id, source)
#             VALUES(%s,%s,%s,%s)"""
#         cursor.execute(sql_insert_click, (time, uuid, product_id, source))
#         conn.commit()
