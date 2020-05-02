"""extensible_celery_worker - Python Celery worker whose registered task list can be extended with
plugins"""

__version__ = '0.1.0-dev3'
__author__ = 'Yann Voté <ygversil@lilo.org>'
__all__ = []


from celery import Celery


app = Celery('default_extensible_celery_worker_app')
