import os


class Config(object):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    ZIP_PATH = BASEDIR + '/app/api/zip/'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ENV = 'development'
    DEBUG = True
    TESTING = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    MONGO_URI = "mongodb://mongo:27017/myDatabase"
