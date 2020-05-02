#!/usr/bin/env python

"""Main module for running extensible_celery_worker."""


from extensible_celery_worker import app


def start_celery_worker():
    """Start the application, that is start the Celery worker."""
    app.worker_main()


main = start_celery_worker


if __name__ == '__main__':
    main()
