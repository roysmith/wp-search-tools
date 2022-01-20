from celery import Celery

app = Celery('tasks',
             broker='redis://tools-redis.svc.eqiad.wmflabs:6379/0',
             backend='redis://tools-redis.svc.eqiad.wmflabs:6379/0')

@app.task
def add(x, y):
    return x + y
