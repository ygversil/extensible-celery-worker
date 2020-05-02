#!/usr/bin/env python

"""Main module for running extensible_celery_worker."""

import argparse

from extensible_celery_worker import app


def _command_line_arguments():
    """Return command-line arguments passed to the worker."""
    parser = argparse.ArgumentParser(prog='excewo', description=(
        'Celery worker whose registered task list can be extended with plugins.'
    ))
    parser.add_argument('-n', '--app-name', help='Name that you give to the Celery application for '
                        'this worker. All tasks for this worker will be prefixed with this name',
                        dest='celery_app_name')
    parser.add_argument('worker_args', help='All remaining arguments after a double dash (--) will '
                        'be passed to the Celery worker. Run `celery worker --help` for details',
                        nargs=argparse.REMAINDER)
    return parser.parse_args()


def start_celery_worker():
    """Start the application, that is start the Celery worker."""
    cli_args = _command_line_arguments()
    if cli_args.celery_app_name:
        app.main = cli_args.celery_app_name
    app.worker_main(argv=['excewo'] + cli_args.worker_args[1:])


main = start_celery_worker


if __name__ == '__main__':
    main()
