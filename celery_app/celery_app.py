from celery import Celery

app = Celery('celery_app',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379',
             include=['celery_app.task_receiver'])
