"""Example tasks for extensible_celery_worker."""


from extensible_celery_worker import app


@app.task
def always_true():
    """Always return ``True``."""
    return True
