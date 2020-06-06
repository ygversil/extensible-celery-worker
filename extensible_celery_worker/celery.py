"""extensible celery worker module to be used when launching directly from Celery."""


from extensible_celery_worker import app  # noqa
from extensible_celery_worker.__main__ import set_up_worker


with set_up_worker():
    pass
