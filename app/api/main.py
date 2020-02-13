from app.api import bp
from app import mongo
from flask import jsonify
from bson import json_util
from app.api.helpers import validate_url
from celery_app.task_receiver import scrap_image

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
    scrap_image.delay(url)

    return str(post_id), 201


@bp.route('/text/<path:url>', methods=['GET'])
@validate_url
def web_text_status(url):
    """Get status of the text download request"""

    return 'text' + url


@bp.route('/text/<path:url>', methods=['POST'])
@validate_url
def web_text_download(url):
    """Text download request"""

    return 'post text' + url


