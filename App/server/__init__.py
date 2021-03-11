from flask import Flask
from config import Config
import os
import pymysql
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager()
jwt.init_app(app)

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

from server.controllers import product_controller, user_controller