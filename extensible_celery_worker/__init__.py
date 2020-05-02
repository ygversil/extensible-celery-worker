"""extensible_celery_worker - Python Celery worker whose registered task list can be extended with
plugins"""

__version__ = '0.1.0-dev5'
__author__ = 'Yann Voté <ygversil@lilo.org>'
__all__ = []


from celery import Celery


DEFAULT_CONFIG = {
    'broker_url': None,
    'result_backend': None,
    'enable_utc': True,
    'timezone': None,
    'worker_send_task_events': True,
    'task_ignore_result': False,
}


app = Celery('default_extensible_celery_worker_app')
