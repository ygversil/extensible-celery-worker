#!/usr/bin/env python

"""Main module for running Flower."""


from functools import partial

from extensible_celery_worker.__main__ import start_daemon


main = partial(start_daemon, 'flower')


if __name__ == '__main__':
    main()
