from app.api import bp
from app import mongo
from flask import jsonify, send_from_directory, current_app
from bson import json_util
from app.api.helpers import validate_url
from config import Config
from celery_app.task_receiver import scrap_image, scrap_text
from bson.objectid import ObjectId
import datetime


@bp.route('/', methods=['GET'])
def index():
    return 'Hello WEB SCRAPER'


@bp.route('/images/all', methods=['GET'])
def images_all():
    """Shows all queries"""
    images = mongo.db.images.find()

    return json_util.dumps(images)


@bp.route('/images/status/<path:data>', methods=['GET'])
def images_status(data):
    """Get status of the images download request"""

    if '/' in data:
        img = mongo.db.images.find({"url": data}, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    elif len(data)==24:
        img = mongo.db.images.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})
    else:
        return jsonify({"error": "URL or ID not found"}), 400
    if img.count() > 0:
        return json_util.dumps(img)
    else:
        return jsonify({"error": "URL or ID not found"}), 400


@bp.route('/images/download/<path:data>', methods=['GET'])
def images_download(data):
    """Download images from saved website"""

    if '/' in data:
        img = mongo.db.images.find({"url": data, }, {"url":1, "status": 1, "_id":1}).sort("date", -1).limit(1)
    elif len(data) == 24:
        img = mongo.db.images.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":1})
    else:
        return jsonify({"error": "URL or ID not found"}), 400
    if img.count() > 0:
        for txt in img:
            if txt['status'] == 'FINISHED':
                filename = str(txt['_id']) + '.zip'

                return send_from_directory(Config['zip_path'], filename, as_attachment=True )
            elif txt['status'] != 'FAILED':
                return jsonify({"error": "NOT READY"}), 400
            else:
                return jsonify({"error": "FAILED, Please Retry"}), 400
    else:
        return jsonify({"error": "URL or ID not found"}), 400


@bp.route('/images/scrap/<path:url>', methods=['POST'])
@validate_url
def web_images_scrap(url):
    """Images download request"""

    image = {
        "url": url,
        "status": "Accepted",
        "directory": "",
        "date": datetime.datetime.utcnow()
    }

    # try ?
    post_id = mongo.db.images.insert_one(image).inserted_id
    scrap_image.delay(url, str(post_id))

    return jsonify({"id": str(post_id)}), 201


@bp.route('/text/status/<path:data>', methods=['GET'])
def web_text_status(data):
    """Get status of the text download request"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data}, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    elif len(data)==24:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})
    else:
        return jsonify({"error": "URL or ID not found"}), 400
    if web_text.count() > 0:
        return json_util.dumps(web_text)
    else:
        return jsonify({"error": "URL or ID not found"}), 400


@bp.route('/text/download/<path:data>', methods=['GET'])
def web_text_download(data):
    """Download text from saved website"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data, }, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    elif len(data) == 24:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})
    else:
        return jsonify({"error": "URL or ID not found"}), 400

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

    return jsonify({"id": str(post_id)}), 201


