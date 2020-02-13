from app import create_app, mongo
import os
import pytest

from pymongo import MongoClient


class TestConfig():
    """Config for test app"""

    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ENV = 'development'
    DEBUG = True
    TESTING = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    MONGO_URI = "mongodb://0.0.0.0:27017/_testingDB"


@pytest.fixture(scope='session')
def db(request):
    """Create the database and the database table"""

    db = MongoClient("mongodb://0.0.0.0:27017/_testingDB")
    mongo = db

    # drop all tables
    def teardown():
        mongo.drop_database('_testingDB')
        mongo.close()

    request.addfinalizer(teardown)
    return mongo


@pytest.fixture(scope='session')
def app(request):
    """Create test app"""

    app = create_app(TestConfig)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    # close app
    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def client(app):
    """Return client app"""
    return app.test_client()

