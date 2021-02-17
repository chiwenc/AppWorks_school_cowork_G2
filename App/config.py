import os
class Config(object):
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/static/assets"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSON_AS_ASCII = False
