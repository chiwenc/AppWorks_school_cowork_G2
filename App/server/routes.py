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
    sql_cmd = """
        select *
        from tracking_realtime 
    """
    return render_template('dashboard.html', last_updated=dir_last_updated('server/static'))

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