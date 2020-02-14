
from celery_app.celery_app import app
import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId
import re


def on_fail(self, exc, task_id, args, kwargs, einfo):
    update_status(args[1], 'FAILED')


def on_retry(self, exc, task_id, args, kwargs, einfo):
    update_status(args[1], 'RETRY')


# auto retry for exception
@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5)
def scrap_image(self, url, UID):
    logging.info(f'Got url {url}')

    return 10


@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5, on_failure=on_fail, on_retry=on_retry)
def scrap_text(self, url, UID):
    logging.info(f'Got url {url}')
    update_status(UID, "Started")

    web_html = requests.get(url).text
    page_text = BeautifulSoup(web_html, "lxml")

    # remove js and style from text
    for script in page_text(["script", "style"]):
        script.decompose()
    text = page_text.get_text()
    text = re.sub("[ \n\r\t]{2,}", "\n", text)

    with MongoClient(Config.MONGO_URI) as mongo:
        mongo.db.web_text.find_one_and_update(
            {'_id': ObjectId(UID)}, {"$set": {'text': text, 'status': "FINISHED"}}
        )
    return 0


def update_status(UID, status):
    """Update status"""
    with MongoClient(Config.MONGO_URI) as mongo:
        mongo.db.web_text.find_one_and_update(
            {'_id': ObjectId(UID)}, {"$set": {'status': status}}
        )


