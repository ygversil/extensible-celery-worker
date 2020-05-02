#!/usr/bin/env python

"""Main module for running extensible_celery_worker."""


from contextlib import contextmanager
import argparse
import logging

from extensible_celery_worker import app


_LOG_LEVEL_MAP = {
    logging.DEBUG: 'DEBUG',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARNING',
    logging.ERROR: 'ERROR',
    logging.CRITICAL: 'CRITICAL',
}


class _StoreLogLevelAction(argparse.Action):
    """``argparse`` action storing an actual ``logging`` log level instead of a string."""

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError('log-level can only be specified once')
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, getattr(logging, values.upper()))


def _command_line_arguments():
    """Return command-line arguments passed to the worker."""
    parser = argparse.ArgumentParser(prog='excewo', description=(
        'Celery worker whose registered task list can be extended with plugins.'
    ))
    parser.add_argument('-n', '--app-name', help='Name that you give to the Celery application for '
                        'this worker. All tasks for this worker will be prefixed with this name',
                        dest='celery_app_name')
    parser.add_argument('-l', '--log-level', help='Log level. The worker process will also use '
                        'this log level (no need to specify `-l` again after `--`)',
                        choices=_LOG_LEVEL_MAP.values(), action=_StoreLogLevelAction)
    parser.add_argument('worker_args', help='All remaining arguments after a double dash (--) will '
                        'be passed to the Celery worker. Run `celery worker --help` for details',
                        nargs=argparse.REMAINDER)
    return parser.parse_args()


@contextmanager
def _log_app(level):
    """Context manager that initialize a basic logging system on startup and ensure it is shutdown
    on exit."""
    level = level or logging.WARNING
    logging.basicConfig(
        level=level,
        format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    )
    yield
    logging.shutdown()


def start_celery_worker():
    """Start the application, that is start the Celery worker."""
    cli_args = _command_line_arguments()
    with _log_app(cli_args.log_level):
        celery_app_name = cli_args.celery_app_name
        if celery_app_name:
            logging.debug('Setting Celery application name to "{}"'.format(celery_app_name))
            app.main = celery_app_name
        worker_args = ['excewo'] + cli_args.worker_args[1:]
        if cli_args.log_level:
            worker_args.extend(['-l', _LOG_LEVEL_MAP[cli_args.log_level]])
        logging.debug('Running Celery worker with arguments: {}'.format(
            ' '.join(worker_args[1:])
        ))
        app.worker_main(argv=worker_args)


main = start_celery_worker


if __name__ == '__main__':
    main()
