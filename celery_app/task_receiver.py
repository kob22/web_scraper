
from celery_app.celery_app import app
import logging


# auto retry for exception
@app.task(bind=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries = 5)
def scrap_image(self, url):
    logging.info(f'Got url {url}')

    return 10