import datetime
from flask import jsonify, send_from_directory, current_app, make_response
from bson import json_util
from bson.objectid import ObjectId
from app.api.helpers import validate_url
from app.api import bp
from app import mongo
from celery_app.task_receiver import scrap_image, scrap_text


@bp.route('/', methods=['GET'])
def index():
    return 'Hello WEB SCRAPER'


@bp.route('/images/all', methods=['GET'])
def images_all():
    """Shows all queries"""
    images = mongo.db.images.find()
    d = json_util.dumps(images)
    # jsonify objectID
    r = make_response( json_util.dumps(images) )
    r.mimetype = 'application/json'

    return r


@bp.route('/images/status/<path:data>', methods=['GET'])
def images_status(data):
    """Get status of the images download request"""

    if '/' in data:
        img = mongo.db.images.find({"url": data}, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    elif len(data) == 24:
        img = mongo.db.images.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)
    if img.count() > 0:
        # jsonify objectID
        r = make_response(json_util.dumps(img))
        r.mimetype = 'application/json'
        return r
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)


@bp.route('/images/download/<path:data>', methods=['GET'])
def images_download(data):
    """Download images from saved website"""

    if '/' in data:
        img = mongo.db.images.find({"url": data, }, {"url":1, "status": 1, "_id":1}).sort("date", -1).limit(1)
    elif len(data) == 24:
        img = mongo.db.images.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":1})
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)
    if img.count() > 0:
        for txt in img:
            if txt['status'] == 'FINISHED':
                filename = str(txt['_id']) + '.zip'
                return send_from_directory(current_app.config['ZIP_PATH'], filename, as_attachment=True)
            if txt['status'] != 'FAILED':
                return make_response(jsonify({"error": "NOT READY"}), 400)
            return make_response(jsonify({"error": "FAILED, Please Retry"}), 400)
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)


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

    return make_response(jsonify({"id": str(post_id)}), 201)


@bp.route('/text/status/<path:data>', methods=['GET'])
def web_text_status(data):
    """Get status of the text download request"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data}, {"url":1, "status": 1, "_id":0}).sort("date", -1).limit(1)
    elif len(data) == 24:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "_id":0})
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)
    if web_text.count() > 0:
        # jsonify objectID
        r = make_response(json_util.dumps(web_text))
        r.mimetype = 'application/json'
        return r

    return make_response(jsonify({"error": "URL or ID not found"}), 400)


@bp.route('/text/download/<path:data>', methods=['GET'])
def web_text_download(data):
    """Download text from saved website"""

    if '/' in data:
        web_text = mongo.db.web_text.find({"url": data, }, {"url":1, "status": 1, "text": 1, "_id":0, }).sort("date", -1).limit(1)
    elif len(data) == 24:
        web_text = mongo.db.web_text.find({'_id': ObjectId(data)}, {"url":1, "status": 1, "text": 1, "_id":0, })
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)

    if web_text.count() > 0:
        for txt in web_text:
            if txt['status'] == 'FINISHED':
                # jsonify objectID
                r = make_response(json_util.dumps(txt['text']))
                r.mimetype = 'application/json'
                return r

            if txt['status'] != 'FAILED':
                return make_response(jsonify({"error": "NOT READY"}), 400)

            return make_response(jsonify({"error": "FAILED, Please Retry"}), 400)
    else:
        return make_response(jsonify({"error": "URL or ID not found"}), 400)


@bp.route('/text/all', methods=['GET'])
def web_text_all():
    """Shows all queries"""
    web_text = mongo.db.web_text.find()

    r = make_response(json_util.dumps(web_text))
    r.mimetype = 'application/json'
    return r


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

    return make_response(jsonify({"id": str(post_id)}), 201)
