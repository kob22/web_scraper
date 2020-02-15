
from celery_app.celery_app import app
import logging
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId
import re
import os
from celery import group, chord
import shutil
import uuid
import imghdr


def on_fail_txt(self, exc, task_id, args, kwargs, einfo):
    """Update status when task fail"""
    update_status_text(args[1], 'FAILED')


def on_retry_txt(self, exc, task_id, args, kwargs, einfo):
    """Update status when taks is waiting for retry"""
    update_status_text(args[1], 'RETRY')


# todo
def on_fail_img(self, exc, task_id, args, kwargs, einfo):
    """Update status when task fail"""
    update_status_images(args[1], 'FAILED')


def on_retry_img(self, exc, task_id, args, kwargs, einfo):
    """Update status when taks is waiting for retry"""
    update_status_images(args[1], 'RETRY')


@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5, on_failure=on_fail_img, on_retry=on_retry_img)
def zip_images(self, res, path_zip, output_path, UID):
    update_status_images(UID, "ZIPPING")
    try:
        shutil.make_archive(output_path, 'zip', path_zip)
    except Exception:
        logging.error("ERROR DURING ZIPPING")
    update_status_images(UID, "FINISHED")


@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5, on_failure=on_fail_img, on_retry=on_retry_img)
def download_image(self, url, temp, path_save):
    """Download image with request get, checks image type """

    img_data = requests.get(url, stream=True)

    # check status code
    if img_data.status_code == 200:
        img_data.raw.decode_content = True

        # generate unique name
        uid = uuid.uuid4()
        temp_name = temp + uid.hex

        # save image in temp dir
        with open(temp_name, 'wb') as img_file:
            img_data.raw.decode_content = True
            shutil.copyfileobj(img_data.raw, img_file)

        # check file type and remove if not img
        extension = imghdr.what(temp_name)
        if extension:
            shutil.move(temp_name, path_save + uid.hex + '.' + extension)
        else:
            os.remove(temp_name)
    elif img_data.status_code == 404:
        logging.info('URL NOT FOUND' + url)
    else:
        logging.error(url)
        raise Exception


# auto retry for exception
@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5, on_failure=on_fail_img, on_retry=on_retry_img)
def scrap_image(self, url, UID):
    logging.info(f'Got url {url} for images scrapping')

    # update status when task start
    update_status_images(UID, "Started")

    protocol = re.match('(?:(?:https?|ftp)://)', url)[0]

    first_slash = url.find('/', len(protocol))
    if first_slash:
        domain_img = url[:first_slash]
    else:
        domain_img = url
    # get webpage and make soup
    web_html = requests.get(url).text
    page_text = BeautifulSoup(web_html, "lxml")

    images = set()

    # get all url images from html
    for img in page_text.findAll('img'):
        img_link = img.get('src')

        if re.match('(?:(?:https?|ftp)://)', img_link):
            images.add(img_link )
        elif img_link.startswith('//'):
            images.add(domain_img + '/' + img_link[2:])
        elif img_link.startswith('/'):
            images.add(domain_img + img_link)
        else:
            images.add(domain_img + '/' + img_link)

    img_path = Config.BASEDIR + '/images/' + UID + '/'
    temp_img_path = Config.BASEDIR + '/temp_images/'
    os.makedirs(img_path, exist_ok=True)
    os.makedirs(temp_img_path, exist_ok=True)

    zip_path = Config.ZIP_PATH + UID
    update_status_images(UID, "DOWNLOADING")
    download_img = chord(download_image.s(x_url, temp_img_path, img_path) for x_url in images)(zip_images.s(img_path, zip_path, UID))


    return 0


@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=5, on_failure=on_fail_txt, on_retry=on_retry_txt)
def scrap_text(self, url, UID):
    logging.info(f'Got url {url} for txt scrapping')
    update_status_text(UID, "Started")

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


def update_status_text(UID, status):
    """Update status"""
    with MongoClient(Config.MONGO_URI) as mongo:
        mongo.db.web_text.find_one_and_update(
            {'_id': ObjectId(UID)}, {"$set": {'status': status}}
        )


def update_status_images(UID, status):
    """Update status"""
    with MongoClient(Config.MONGO_URI) as mongo:
        mongo.db.images.find_one_and_update(
            {'_id': ObjectId(UID)}, {"$set": {'status': status}}
        )
