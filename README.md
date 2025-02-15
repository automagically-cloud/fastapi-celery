# Asynchronous Tasks with FastAPI and Celery

Example of how to handle background processes with FastAPI, Celery, and Docker.

## Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/fastapi-and-celery/).

## Want to use this project?

Spin up the containers:

```sh
docker-compose up -d --build
```

Open your browser to [http://localhost:8004](http://localhost:8004) to view the app or to [http://localhost:5556](http://localhost:5556) to view the Flower dashboard.

Trigger a new task:

```sh
curl http://localhost:8004/tasks -H "Content-Type: application/json" --data '{"type": 0}'
```

Check the status:

```sh
curl http://localhost:8004/tasks/<TASK_ID>
```

<https://liftoffllc.medium.com/creating-a-truly-distributed-microservice-architecture-with-celery-and-docker-swarm-e178198e6838>
<https://render.com/docs/deploy-celery>

## Celery Knowledge base

### `bind=True`

<https://stackoverflow.com/questions/54899320/what-is-the-meaning-of-bind-true-keyword-in-celery>

### Celery logging

<https://docs.celeryq.dev/en/stable/internals/reference/celery.utils.log.html>
