from celery import Celery
from config import REDIS_URL_CELERY


config = {
    'CELERY_BROKER_URL': REDIS_URL_CELERY,
    'CELERY_RESULT_BACKEND': REDIS_URL_CELERY,
}
celery = Celery('tasks', broker=config['CELERY_BROKER_URL'])

celery.conf.update(config)



