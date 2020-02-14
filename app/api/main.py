from app.api import bp
from app import mongo
from flask import jsonify
from bson import json_util
from app.api.helpers import validate_url
from celery_app.task_receiver import scrap_image, scrap_text
from bson.objectid import ObjectId
import datetime


@bp.route('/', methods=['GET'])
def index():
    return 'Hello WEB SCRAPER'


@bp.route('/images/<path:url>', methods=['GET'])
@validate_url
def web_images_status(url):
    """Get status of the image download request"""

    images_status = mongo.db.images.find({"url": url}).sort("date", -1).limit(1)
    if images_status.count() > 0:
        return json_util.dumps(images_status)
    else:
        return jsonify({"error": "URL not found"}), 400


@bp.route('/images/<path:url>', methods=['POST'])
@validate_url
def web_images_download(url):
    """Images download request"""

    image = {
        "url": url,
        "status": "Accepted",
        "images": [],
        "date": datetime.datetime.utcnow()
    }

    # try ?
    post_id = mongo.db.images.insert_one(image).inserted_id
    scrap_image.delay(url, str(post_id))

    return str(post_id), 201


@bp.route('/text/status/<path:data>', methods=['GET'])
def web_text_status(data):
    """Get status of the text download request"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data}, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    else:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})

    if web_text.count() > 0:
        return json_util.dumps(web_text)
    else:
        return jsonify({"error": "URL or ID not found"}), 400


@bp.route('/text/download/<path:data>', methods=['GET'])
def web_text_download(data):
    """Download text from saved website"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data, }, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    else:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})

    if web_text.count() > 0:
        for txt in web_text:
            if txt['status'] == 'FINISHED':
                return json_util.dumps(txt)
            elif txt['status'] != 'FAILED':
                return jsonify({"error": "NOT READY"}), 400
            else:
                return jsonify({"error": "FAILED, Please Retry"}), 400
    else:
        return jsonify({"error": "URL or ID not found"}), 400


@bp.route('/text/all', methods=['GET'])
def web_text_all():
    """Shows all queries"""
    web_text = mongo.db.web_text.find()

    return json_util.dumps(web_text)


@bp.route('/text/scrap/<path:url>', methods=['POST'])
@validate_url
def web_text_scrap(url):
    """Text download request"""
    web_text = {
        "url": url,
        "status": "Accepted",
        "text": "",
        "date": datetime.datetime.utcnow()
    }

    post_id = mongo.db.web_text.insert_one(web_text).inserted_id

    scrap_text.delay(url, str(post_id))

    return 'post text' + url, 201


