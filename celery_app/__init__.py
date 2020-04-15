from celery import Celery
from config import REDIS_URL_CELERY


config = {
    'CELERY_BROKER_URL': REDIS_URL_CELERY,
    'CELERY_RESULT_BACKEND': REDIS_URL_CELERY,
    'CELERYD_CONCURRENCY':10, # 并发worker数
    'CELERYD_FORCE_EXECV': True, # 非常重要,有些情况下可以防止死锁
    'CELERYD_MAX_TASKS_PER_CHILD': 100, # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
    'CELERY_DISABLE_RATE_LIMITS': True, # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行

}
celery = Celery('tasks', broker=config['CELERY_BROKER_URL'])

celery.conf.update(config)



