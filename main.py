from celery.result import AsyncResult
from fastapi import Body, FastAPI
from fastapi.responses import JSONResponse


from worker import create_task, error_task, create_shared_task, task_autoretry
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
import os

app = FastAPI()


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

    sentry_sdk.set_context("service", {"slug": "celery-test", "worker": False})

    print("Initialized Sentry in main!")



@app.post("/tasks", status_code=201)
def run_create_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})

@app.post("/error_tasks", status_code=201)
def run_error_task(payload = Body(...)):
    task_type = payload["type"]
    task = error_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})

@app.post("/shared_tasks", status_code=201)
def run_create_shared_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_shared_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})

@app.post("/autoretry_tasks", status_code=201)
def run_task_autoretry(payload = Body(...)):
    task_type = payload["type"]
    task = task_autoretry.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)
