import os
import time

from celery import Celery, signals

import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
import os
from celery.signals import celeryd_init


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@signals.celeryd_init.connect
def init_sentry(**_kwargs):

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
        )

        sentry_sdk.set_context("service", {"slug": "celery-test", "worker": True})

        print("Initialized Sentry in worker!")


@celeryd_init.connect(sender='worker12@example.com')
@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    sentry_sdk.init(dsn="...")


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@celery.task(name="error_task")
def error_task(task_type):
    time.sleep(int(task_type) * 10)
    1/0
    return True
