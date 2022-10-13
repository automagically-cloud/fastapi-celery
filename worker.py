import os
import queue
import time
import random 

from celery import Celery, signals, shared_task

import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
import os
from celery.utils.log import get_task_logger

CELERY_WORKER_NAME = os.environ.get("CELERY_WORKER_NAME", None)
CELERY_WORKER_LOGLEVEL = os.environ.get("CELERY_WORKER_LOGLEVEL", None)
CELERY_WORKER_CONCURRENCY = os.environ.get("CELERY_WORKER_CONCURRENCY", None)
CELERY_WORKER_QUEUES = os.environ.get("CELERY_WORKER_QUEUES", None)
CELERY_TEST_QUEUE = os.environ.get("CELERY_TEST_QUEUE", "test")


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


logger = get_task_logger(__name__)

# TODO: Check if we should use other signals for reasons

# @signals.after_setup_logger.connect()
# def after_setup_logger(**_kwargs):
#     print("after_setup_logger")

# @signals.worker_init.connect()
# def worker_init_test(**_kwargs):
#     print("worker_init_test")

@signals.worker_init.connect()
def init_sentry(**_kwargs):
    print("init_sentry")

    SENTRY_DSN = os.environ.get("SENTRY_DSN", None)


    if SENTRY_DSN:

        SENTRY_DEBUG = os.environ.get("SENTRY_DEBUG", False)

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                CeleryIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=0.0,
            debug=SENTRY_DEBUG
        )

        sentry_sdk.set_context("worker", {
            "name": CELERY_WORKER_NAME,
            "loglevel": CELERY_WORKER_LOGLEVEL,
            "concurrency": CELERY_WORKER_CONCURRENCY,
            "queues": CELERY_WORKER_QUEUES,
        })

    else:
        print("No SENTRY_DSN found!")



@celery.task(queue=CELERY_TEST_QUEUE)
def create_task(task_type):

    logger.info(f"create_task run: {task_type}")

    time.sleep(int(task_type) * 10)

    return True


@celery.task(queue=CELERY_TEST_QUEUE)
def error_task(task_type):

    logger.info(f"error_task run: {task_type}")

    time.sleep(int(task_type) * 10)
    1/0

    return True


@shared_task(queue=CELERY_TEST_QUEUE)
def create_shared_task(task_type):

    logger.info(f"create_shared_task run: {task_type}")

    time.sleep(int(task_type) * 10)
    return True


@shared_task(bind=True, queue=CELERY_TEST_QUEUE, autoretry_for=(Exception,), retry_kwargs={'max_retries': 7, 'countdown': 5})
def task_autoretry(self):

    logger.info(f"task_autoretry run: {self.request.id}")

    if not random.choice([0, 1]):
        raise Exception()

    return True

@celery.task(bind=True, queue=CELERY_TEST_QUEUE, max_retries=5)
def retrying(self):

    logger.info(f"retrying: {self.request.id}")

    try:
        return 1/0
    except Exception:
        self.retry(countdown=5)


@celery.task(bind=True, queue=CELERY_TEST_QUEUE)
def show_progress(self, n):

    logger.info(f"show_progress: {self.request.id}")

    for i in range(n):
        time.sleep(3)
        self.update_state(state='PROGRESS', meta={'current': i, 'total': n})

    return {'current': n, 'total': n}