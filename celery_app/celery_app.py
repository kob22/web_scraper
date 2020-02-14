from celery import Celery

app = Celery('celery_app',
             broker='redis://redis:6379',
             backend='redis://redis:6379',
             include=['celery_app.task_receiver'])
