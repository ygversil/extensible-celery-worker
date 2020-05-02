extensible_celery_worker
========================

.. image:: https://img.shields.io/pypi/v/extensible_celery_worker.svg
    :target: https://pypi.python.org/pypi/extensible_celery_worker
    :alt: Latest PyPI version

.. image:: https://travis-ci.com/ygversil/extensible-celery-worker.svg?branch=master
   :target: https://travis-ci.com/github/ygversil/extensible-celery-worker
   :alt: Latest Travis CI build status

Python Celery worker whose registered task list can be extended with plugins

Overview
--------

`extensible_celery_worker` is a `Celery`_ daemon running an `application`_ with a `worker`_.
However, by itself this worker has no tasks. You can add `tasks`_ by installing plugins. In this
manner, you compose Celery applications which suit your very specific needs.

See the `Celery tutorial`_ for an introduction to Celery, Celery applications, tasks and workers.

Installation
------------

Install with pip::

    pip install extensible_celery_worker

However, this library is not really useful if installed alone. You should install one or more
plugins that add Celery tasks so that useful things can be done by the worker.

Licence
-------

MIT License. See the ``LICENSE`` file.

Authors
-------

`extensible_celery_worker` was written by `Yann Voté <ygversil@lilo.org>`_.

.. _Celery: http://www.celeryproject.org/

.. _application: https://docs.celeryproject.org/en/latest/userguide/application.html

.. _worker:  https://docs.celeryproject.org/en/latest/userguide/workers.html

.. _tasks: https://docs.celeryproject.org/en/latest/userguide/tasks.html

.. _Celery tutorial: https://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#first-steps
