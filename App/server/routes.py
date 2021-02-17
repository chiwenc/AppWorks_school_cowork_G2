from server import app
import bcrypt
from collections import defaultdict
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pymysql
import os
import random
from server.user import get_user, create_user
from server.products import get_products, get_products_variants, create_product
from server.tracking import get_user_behavior_by_date
from itertools import groupby
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

PAGE_SIZE = 6
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))

@app.route('/signin.html', methods=['GET'])
def signin_page():
    return render_template('signin.html', last_updated=dir_last_updated('server/static'))

@app.route('/signup.html', methods=['GET'])
def signup_page():
    return render_template('signup.html', last_updated=dir_last_updated('server/static'))

@app.route('/profile.html', methods=['GET'])
def profile_page():
    return render_template('profile.html', last_updated=dir_last_updated('server/static'))

@app.route('/api/1.0/signin', methods=['POST'])
def signin():
    form = request.form.to_dict()
    email = form.get('email', None) 
    password = form.get('password', None)

    user = get_user(email)
    if not user:
        return jsonify({"error": "Bad username"}), 401

    if not check_password(password, user["password"]):
        return jsonify({"error": "Bad password"}), 401

    access_token = create_access_token(identity=user["name"])
    return {
        "access_token": access_token,
        "access_expired": 3600,
        "user": {
            "id": user["id"],
            "rovider": 'native',
            "name": user["name"],
            "email": email,
            "picture": ""
        }
    }

@app.route('/api/1.0/signup', methods=['POST'])
def signup():
    form = request.form.to_dict()
    name = form.get('name', None)
    email = form.get('email', None) 
    password = form.get('password', None)
    encrypted_password = get_hashed_password(password)

    user = get_user(email)
    if user:
        return jsonify({"error": "User already existed"}), 401

    access_token = create_access_token(identity=name)
    user_id = create_user('native', email, encrypted_password, name, access_token, 2592000)
    return {
        "access_token": access_token,
        "access_expired": 3600,
        "user": {
            "id": user_id,
            "rovider": 'native',
            "name": name,
            "email": email,
            "picture": ""
        }
    }

@app.route('/api/1.0/profile', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    print(current_user)
    return f"Welcome! {current_user}"

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', last_updated=dir_last_updated('server/static'))

from time import sleep
@app.route('/sleep')
def long_running():
    sleep(10)
    return "Wake up!"

@app.route('/api/1.0/user/behavior/<date>')
def api_get_user_behavior(date):
    data = get_user_behavior_by_date(date)
    if (data):
        return {
            "behavior_count": [data['view_count'], data['view_item_count'], data['add_to_cart_count'], data['checkout_count']],
            "user_count": [data['unique_user_count'], data['new_user_count'], data['return_user_count']]
        }
    else:
        return {
            "behavior_count": [0, 0, 0, 0],
            "user_count": [0, 0, 0]
        }

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def find_product(category, paging):
    if (category == 'all') :
        return get_products(PAGE_SIZE, paging)
    elif (category in ['men', 'women', 'accessories']):
        return get_products(PAGE_SIZE, paging, {"category": category})
    elif (category == 'search'):
        keyword = request.values["keyword"]
        if (keyword):
            return get_products(PAGE_SIZE, paging, {"keyword": keyword})
    elif (category == 'details'):
        product_id = request.values["id"]
        return get_products(PAGE_SIZE, paging, {"id": product_id})
    elif (category == 'recommend'):
        product_id = request.values["id"]
        return get_products(3, paging, {"recommend": product_id})

def get_products_with_detail(url_root, products):
    product_ids = [p["id"] for p in products]
    variants = get_products_variants(product_ids)
    variants_map = defaultdict(list)
    for variant in variants:
        variants_map[variant["product_id"]].append(variant)

    def parse(product, variants_map):
        product_id = product["id"]
        image_path = url_root + 'static/assets/' + str(product_id) + '/'
        product["main_image"] = image_path + product["main_image"]
        product["images"] = [image_path + img for img in product["images"].split(',')]
        product_variants = variants_map[product_id]
        if (not product_variants):
            return product

        product["variants"] = [
            {
                "color_code": v["color_code"],
                "size": v["size"],
                "stock": v["stock"]
            }
            for v in product_variants
        ]
        colors = [
            {
                "code": v["color_code"],
                "name": v["color_name"]
            }
            for v in product_variants
        ]
        product["colors"] = list({c['code'] + c["name"]: c for c in colors}.values())
        product["sizes"] = list(set([
            v["size"]
            for v in product_variants   
        ]))
        return product

    return [
        parse(product, variants_map) for product in products
    ]

@app.route('/api/1.0/products/<category>', methods=['GET'])
def api_get_products(category):
    paging = request.values.get('paging') or 0
    paging = int(paging)
    res = find_product(category, paging)

    if (not res):
        return {"error":'Wrong Request'}

    products = res.get("products")
    product_count = res.get("product_count")

    if (not products):
        return {"error":'Wrong Request'}
    
    if (not len(products)):
        if (category == 'details'):
            return {"data": None}
        else:
            return {"data": []}

    products_with_detail = \
        get_products_with_detail(request.url_root, products) if products[0]["source"] == 'native' else products
    if (category == 'details'):
        products_with_detail = products_with_detail[0]

    result = {}
    if (product_count > (paging + 1) * PAGE_SIZE):
        result = {
            "data": products_with_detail,
            "next_paging": paging + 1
        } 
    else: 
        result = {"data": products_with_detail}
    
    return result

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/admin/product.html', methods=['GET'])
def admin_product():
    return render_template('product_create.html')

def save_file(folder, file):
    folder_root = app.root_path + app.config['UPLOAD_FOLDER']
    folder_path = folder_root + '/' + folder
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            folder_path,
            filename
        ))
        return filename
    else:
        return None

@app.route('/api/1.0/product', methods=['POST'])
def api_create_product():
    form = request.form.to_dict()
    product_id = form["product_id"]
    main_image = request.files.get("main_image")
    main_image_name = save_file(product_id, main_image)
    other_images = request.files.getlist('other_images')
    other_images_names = []
    for file in other_images:
        other_images_names.append(save_file(product_id, file))

    product = {
        'id': form['product_id'],
        'category': form['category'],
        'title': form['title'],
        'description': form['description'],
        'price': int(form['price']),
        'texture': form['texture'],
        'wash': form['wash'],
        'place': form['place'],
        'note': form['note'],
        'story': form['story'],
        'main_image': main_image_name,
        'images': ','.join(other_images_names),
        'source': 'native'
    }

    variants = [   
        {
            "size": size,
            "color_code": color_code,
            "color_name": color_name,
            "stock": random.randint(1,10),
            "product_id": product_id
        }
        for (color_code, color_name) 
        in zip(form["color_codes"].split(','), form["color_names"].split(','))
        for size
        in form["sizes"].split(',')
    ]

    create_product(product, variants)
    return "Ok"

@app.route('/recommendation')
def product_recommendation():
    res = get_products(100, 0, {"source": "amazon"},)
    return render_template('product_recommendation.html', products = [{"id": p["id"], "title": p["title"]} for p in res["products"]])
