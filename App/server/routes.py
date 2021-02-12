from server import app

from flask import Flask, render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from server import db

import os
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', last_updated=dir_last_updated('server/static'))

@app.route('/products')
def products():
    select_products_sql = " \
        SELECT item_id, title FROM amazon_product \
    "
    query_data = db.engine.execute(select_products_sql)
    products = query_data.fetchall()
    print(products)
    return render_template('products.html', products = products)

@app.route('/api/1.0/user/behavior/<date>')
def user_behavior(date):
    print(date)
    select_analysis_sql = """
        SELECT *
        FROM tracking_analysis
        WHERE date = %s
    """

    query_data = db.engine.execute(select_analysis_sql, date + ' 00:00:00')
    data = query_data.fetchone()

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

@app.route('/api/1.0/user/product/<id>')
def get_products(id):
    res = db.engine.execute("SELECT * FROM amazon_product WHERE item_id = %s", id)
    product = res.fetchone()
    return {
        "item_id": product["item_id"],
        "title": product["title"],
        "image": product["image"] 
    }

@app.route('/api/1.0/user/product/<id>/recommend')
def get_recommend_products(id):
    res = db.engine.execute("\
        SELECT * FROM amazon_product \
        INNER JOIN similarity_model ON amazon_product.item_id = similarity_model.item2_id \
        WHERE similarity_model.item1_id = %s \
        ORDER BY similarity DESC \
        LIMIT 3",
        id
    )
    products = [
        {
            "item_id": p["item_id"],
            "title": p["title"],
            "image": p["image"] 
        }
        for p in res.fetchall()
    ]
    return {"data": products}