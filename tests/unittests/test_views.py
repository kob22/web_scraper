from app.api.main import index, images_all, images_status, images_download, web_images_scrap
from unittest.mock import patch, MagicMock, Mock
from bson import json_util
from bson import ObjectId
import datetime
import pytest
from app import create_app
import json
import os
from app.api import main
from pymongo.results import InsertOneResult


class FakeCursor(list):
    """Fake cursorDB with count method"""

    def count(self):
        return self.__len__()


class TestConfig():
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    ZIP_PATH = BASEDIR + '/app/api/zip/'


@pytest.fixture(scope="function")
def app_context():
    app = create_app(TestConfig)
    app_context = app.app_context()
    app_context.push()
    yield

    app_context.pop()


def test_index():
    assert 'Hello WEB SCRAPER' == index()


@patch('app.api.main.mongo')
def test_images_all_with_entries(mock_requests, app_context):
    images_all_data = [
        {'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FAILED', 'directory': '',
         'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)},
        {'_id': ObjectId('5eac0f202775ac1aa947a82d'), 'url': 'https://edition.cnn.com/', 'status': 'FINISHED',
         'directory': '', 'date': datetime.datetime(2020, 5, 1, 11, 59, 28, 686000)}]

    mock_requests.db.images.find.return_value = images_all_data
    response = images_all()

    # decode ObjectId to json and loads
    images_all_data_json = json_util.dumps(images_all_data)
    images_all_data_decoded = json.loads(images_all_data_json)

    assert response.json == images_all_data_decoded
    assert response.mimetype == 'application/json'
    assert response.status_code == 200
    mock_requests.db.images.find.assert_called_once()


@patch('app.api.main.mongo')
def test_images_all_without_entries(mock_requests, app_context):
    images_all_data = []
    mock_requests.db.images.find.return_value = images_all_data
    response = images_all()
    assert response.json == images_all_data
    assert response.mimetype == 'application/json'
    assert response.status_code == 200
    mock_requests.db.images.find.assert_called_once()


@patch('pymongo.cursor.Cursor.limit')
def test_images_status_no_url_inDB(mock_limit, app_context):
    no_entries = FakeCursor([])
    mock_limit.return_value = no_entries
    url = 'http://fakeurl.pl/'
    response = images_status(url)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400
    mock_limit.assert_called_once()


@patch('pymongo.collection.Collection.find')
def test_images_status_no_hash_inDB(mock_limit, app_context):
    no_entries = FakeCursor([])
    mock_limit.return_value = no_entries
    hash = '5eac0f092775ac1aa947a82c'
    response = images_status(hash)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400
    mock_limit.assert_called_once()


def test_images_status_wrong_data_in_url(app_context):
    hash = '5eac0f092775ac1aa947'
    response = images_status(hash)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400

@patch('pymongo.cursor.Cursor.limit')
def test_images_status_url_inDB(mock_limit, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FAILED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)
    mock_limit.return_value = entries
    url = 'http://google.pl'

    # decode ObjectId to json and loads
    entry_json = json_util.dumps(entry)
    entry_decoded = json.loads(entry_json)

    response = images_status(url)
    assert response.json == entry_decoded
    assert response.mimetype == 'application/json'
    assert response.status_code == 200
    mock_limit.assert_called_once()


@patch('pymongo.collection.Collection.find')
def test_images_status_hash_inDB(mock_find, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FAILED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)
    mock_find.return_value = entries
    hash = '5eac0f092775ac1aa947a82c'

    # decode ObjectId to json and loads
    entry_json = json_util.dumps(entry)
    entry_decoded = json.loads(entry_json)

    response = images_status(hash)
    assert response.json == entry_decoded
    assert response.mimetype == 'application/json'
    assert response.status_code == 200

    mock_find.assert_called_once()


@patch('pymongo.cursor.Cursor.limit')
def test_images_download_no_url_inDB(mock_limit, app_context):
    no_entries = FakeCursor([])
    mock_limit.return_value = no_entries
    url = 'http://fakeurl.pl/'
    response = images_download(url)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400
    mock_limit.assert_called_once()


@patch('pymongo.collection.Collection.find')
def test_images_download_no_hash_inDB(mock_limit, app_context):
    no_entries = FakeCursor([])
    mock_limit.return_value = no_entries
    hash = '5eac0f092775ac1aa947a82c'
    response = images_download(hash)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400
    mock_limit.assert_called_once()


def test_images_download_wrong_data_in_url(app_context):
    hash = '5eac0f092775ac1aa947'
    response = images_download(hash)
    assert response.json == {'error': 'URL or ID not found'}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400

@patch('pymongo.cursor.Cursor.limit')
def test_images_download_url_failed(mock_limit, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FAILED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)

    mock_limit.return_value = entries
    url = 'http://google.pl'
    response = images_download(url)
    assert response.json == {"error": "FAILED, Please Retry"}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400

    mock_limit.assert_called_once()

@patch('pymongo.cursor.Cursor.limit')
def test_images_download_url_failed(mock_limit, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'Accepted', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)

    mock_limit.return_value = entries
    url = 'http://google.pl'
    response = images_download(url)
    assert response.json == {"error": "NOT READY"}
    assert response.mimetype == 'application/json'
    assert response.status_code == 400

    mock_limit.assert_called_once()


@patch('app.api.main.send_from_directory')
@patch('pymongo.cursor.Cursor.limit')
def test_images_download_url_finished(mock_limit, mock_send_from, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FINISHED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)

    mock_limit.return_value = entries

    url = 'http://google.pl'
    response = images_download(url)
    filename = str(entry[0]['_id']) + '.zip'
    mock_limit.assert_called_once()
    mock_send_from.assert_called_with(TestConfig.ZIP_PATH, filename, as_attachment=True)

@patch('app.api.main.send_from_directory')
@patch('pymongo.cursor.Cursor.limit')
def test_images_download_url_finished(mock_limit, mock_send_from, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FINISHED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)

    mock_limit.return_value = entries

    url = 'http://google.pl'
    response = images_download(url)
    filename = str(entry[0]['_id']) + '.zip'
    mock_limit.assert_called_once()
    mock_send_from.assert_called_with(TestConfig.ZIP_PATH, filename, as_attachment=True)

@patch('app.api.main.send_from_directory')
@patch('pymongo.collection.Collection.find')
def test_images_download_hash_finished(mock_find, mock_send_from, app_context):
    entry = [{'_id': ObjectId('5eac0f092775ac1aa947a82c'), 'url': 'http://google.pl', 'status': 'FINISHED', 'directory': '',
            'date': datetime.datetime(2020, 5, 1, 11, 59, 5, 887000)}]

    entries = FakeCursor(entry)
    hash = '5eac0f092775ac1aa947a82c'
    mock_find.return_value = entries

    response = images_download(hash)
    filename = str(entry[0]['_id']) + '.zip'
    mock_find.assert_called_once()
    mock_send_from.assert_called_with(TestConfig.ZIP_PATH, filename, as_attachment=True)

@patch.object(main.datetime, 'datetime', Mock(wraps=datetime.datetime))
@patch('app.api.main.scrap_image')
@patch('app.api.main.mongo')
def test_scrap_images_request(mock_insert, mock_scrap_image, app_context):

    url = 'http://google.pl'
    generate_id = ObjectId()
    mock_insert.db.images.insert_one.return_value = InsertOneResult(generate_id, False)
    time = datetime.datetime(1990, 1, 1)
    main.datetime.datetime.utcnow.return_value = time

    image = {
        "url": url,
        "status": "Accepted",
        "directory": "",
        "date": time
    }

    response = web_images_scrap(url)

    mock_insert.db.images.insert_one.assert_called_with(image)
    assert response.json == {"id": str(generate_id)}
    assert response.mimetype == 'application/json'
    assert response.status_code == 201

