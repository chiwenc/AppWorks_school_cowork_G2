from flask import Flask
from config import Config
import os
import pymysql
from flask_jwt_extended import JWTManager
from waitress import serve

app = Flask(__name__)
app.config.from_object(Config)


jwt = JWTManager()
jwt.init_app(app)

conn = pymysql.connect(
    host = app.config["DB_HOST"],
    user = app.config["DB_USERNAME"],
    password = app.config["DB_PASSWORD"],
    database = app.config["DB_DATABASE"],
    cursorclass = pymysql.cursors.DictCursor
)

from server.controllers import product_controller, user_controller
