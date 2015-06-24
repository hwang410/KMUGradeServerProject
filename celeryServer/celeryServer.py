from __future__ import absolute_import
from celery import Celery

app = Celery('tasks', broker = 'redis://192.168.0.8:6379', include=['tasks'])
#test
if __name__ == '__main__':
    app.start()
