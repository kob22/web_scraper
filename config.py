import os


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ENV = 'development'
    DEBUG = True
    TESTING = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    MONGO_URI = "mongodb://0.0.0.0:27017/myDatabase"
