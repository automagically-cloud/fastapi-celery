import os
import time

from celery import Celery, signals

import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
import os
from celery.signals import celeryd_init, worker_init, after_setup_logger

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

print("print works in worker.py")

@signals.after_setup_logger
def after_setup_logger(**_kwargs):
    print("after_setup_logger")

@signals.worker_init.connect
def worker_init_test(**_kwargs):
    print("worker_init_test")

@signals.worker_init.connect
def init_sentry(**_kwargs):
    print("init_sentry")

    SENTRY_DSN = os.environ.get("SENTRY_DSN", None)

    if SENTRY_DSN:

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                CeleryIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
            debug=True
        )

        sentry_sdk.set_context("service", {"slug": "celery-test", "worker": True})

        print("Initialized Sentry in worker!")

    else:
        print("No SENTRY_DSN found!")


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@celery.task(name="error_task")
def error_task(task_type):
    time.sleep(int(task_type) * 10)
    1/0
    return True
