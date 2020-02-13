from celery import Celery

app = Celery('celery_app',
             broker='pyamqp://guest@localhost//',
             backend='rpc://',
             include=['celery_app.task_receiver'])