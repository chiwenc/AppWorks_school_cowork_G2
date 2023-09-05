import bcrypt
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server import app
from ..models.user_model import get_user, create_user, get_user_by_name
from ..models.tracking_model import get_user_behavior_by_date
from ..utils.util import dir_last_updated
from pytz import timezone
import json
import pymysql
import datetime
import uuid
from config import Config
import uuid
from datetime import datetime
from pytz import timezone

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
    user = get_user_by_name(current_user)
    # msg for expired token: {"msg": "Token has expired"}
    # return f"Welcome! {current_user}"
    return {"data": {
        "provider": "native",
        "name": current_user,
        "email": user["email"],
        "picture": ""}
    }


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
    action_from = request.values.get("action_from")
    action_to = request.values.get("action_to")
    source = request.values.get("source")
    
    current_time = datetime.datetime.now()
    utc8_time = current_time.astimezone(timezone('Asia/Taipei'))
    
    conn = pymysql.connect(**mysql_config.db_config)    
    with conn.cursor() as cursor:
        sql_insert_tracking = """
            INSERT INTO tracking (uuid, event_type, action_from, action_to, source, time)
            VALUES(%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql_insert_tracking, (uuid, event_type, action_from, action_to, source, utc8_time))
        conn.commit()
    return "Successfully capture user behavior.", 200


@app.route('/api/1.0/order/checkout', methods=["POST"])
def api_checkout():
    order_id = uuid.uuid4()
    order_time = datetime.now()

    form = request.get_data()
    form = json.loads(form)
    prime = form["prime"]
    shipping = form["order"]["shipping"]
    payment = form["order"]["payment"]
    subtotal = form["order"]["subtotal"]
    freight = form["order"]["freight"]
    total = form["order"]["total"]
    name = form["order"]["recipient"]["name"]
    phone = form["order"]["recipient"]["phone"]
    email = form["order"]["recipient"]["email"]
    address = form["order"]["recipient"]["address"]
    time = form["order"]["recipient"]["time"]
    user_id = form["order"]["recipient"]["user_id"]
    items = form["order"]["list"]
    connection = pymysql.connect(**mysql_config.db_config)
    with connection.cursor() as cursor:
        for item in items:
            product_id = item["id"]
            product_name = item["name"]
            product_price = item["price"]
            product_color_name = item["color"]["name"]
            product_color_code = item["color"]["code"]
            product_size = item["size"]
            product_qty = item["qty"]
            cursor.execute('INSERT INTO order_history (order_id, order_time, user_id, prime, shipping, payment, '
                           'subtotal, freight, total, name, phone, email, address, time, product_id, product_name, '
                           'price, color_name, color_code, size, qty) '
                           'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (order_id, order_time, user_id, prime, shipping, payment, subtotal, freight, total,
                            name, phone, email, address, time, product_id, product_name, product_price,
                            product_color_name, product_color_code, product_size, product_qty))
    connection.commit()
    return {"data": {"number": order_id}}


@app.route('/api/1.0/uuid', methods=["GET"])
def generate_uuid():
    conn = pymysql.connect(**mysql_config.db_config)
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM uuid_source")
        source = "A" if cursor.fetchone()[0] % 2 == 0 else "B"
        _id = uuid.uuid4()
        cursor.execute("INSERT INTO uuid_source (uuid, source) VALUES (%s, %s)",
                       (_id, source))
        conn.commit()
    return {"uuid": _id, "source": source}
