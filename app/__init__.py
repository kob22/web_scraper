from flask import Flask
from config import Config
from pymongo import MongoClient

mongo = MongoClient(Config.MONGO_URI)


def create_app(config_class=Config):
    """Creates and return flask app"""

    # new flask app from config
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
