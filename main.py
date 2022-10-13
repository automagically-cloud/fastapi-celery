from celery.result import AsyncResult
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse


from worker import create_task, error_task, create_shared_task, task_autoretry, retrying, show_progress
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
import os

app = FastAPI()

SERVICE_SLUG = os.environ.get("SERVICE_SLUG", None)
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

    sentry_sdk.set_context("service", {"slug": SERVICE_SLUG})


@app.post("/tasks/{n}", status_code=201)
def run_create_task(n: int):
    task = create_task.delay(n)
    return JSONResponse({"task_id": task.id})

@app.post("/error/{n}", status_code=201)
def run_error_task(n: int):
    task = error_task.delay(n)
    return JSONResponse({"task_id": task.id})

@app.post("/shared_task/{n}", status_code=201)
def run_create_shared_task(n: int):
    task = create_shared_task.delay(n)
    return JSONResponse({"task_id": task.id})

@app.post("/autoretry", status_code=201)
def run_task_autoretry():
    task = task_autoretry.delay()
    return JSONResponse({"task_id": task.id})

@app.post("/retrying", status_code=201)
def run_task_retrying():
    task = retrying.delay()
    return JSONResponse({"task_id": task.id})

@app.post("/show_progress/{n}", status_code=201)
def run_task_show_progress(n: int):
    task = show_progress.delay(n)
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
        "task_queue": task_result.queue
    }

    return JSONResponse(result)
