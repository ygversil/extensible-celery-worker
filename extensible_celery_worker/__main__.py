#!/usr/bin/env python

"""Main module for running extensible_celery_worker."""


from contextlib import contextmanager
import argparse
import configparser
import logging


try:
    from flower.command import FlowerCommand
except ImportError:
    FlowerCommand = None
from stevedore import extension

from extensible_celery_worker import DEFAULT_CONFIG, app
from extensible_celery_worker.config_paths import config_paths


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
    parser.add_argument('--config', help='Path to a configuration file for the Celery application '
                        'and worker (Python file). No need to specify `--config` again after `--`',
                        dest='celery_app_config')
    parser.add_argument('-a', '--app-config', help='Path to a configuration file for '
                        'extensible_celery_worker (INI-style).', dest='cli_config_path')
    parser.add_argument('-l', '--log-level', help='Log level. The worker process will also use '
                        'this log level (no need to specify `-l` again after `--`)',
                        choices=_LOG_LEVEL_MAP.values(), action=_StoreLogLevelAction)
    subparsers = parser.add_subparsers(title='Commands', dest='command', help='Available commands')
    subparsers.required = True
    worker_parser = subparsers.add_parser('worker', help='Start worker')
    worker_parser.add_argument('worker_args', help='All remaining arguments after a double dash '
                               '(--) will be passed to the Celery worker. Run `celery worker '
                               '--help` for details',
                               nargs=argparse.REMAINDER)
    if FlowerCommand is not None:
        subparsers.add_parser('flower', help='Start flower')
    return parser.parse_args()


@contextmanager
def _celery_app_config(cli_config_path=None):
    """Context manager that returns a ``ConfigParser`` instance after reading configuration from
    all expected paths.

    On exit, it ensures that the config is cleared.
    """
    config = configparser.ConfigParser()
    used_config_files = config.read(path.as_posix() for path in config_paths(cli_config_path))
    logging.info('Found and used configuration files (in override order, next overrides previous): '
                 '{}'.format(', '.join(used_config_files)))
    yield config
    config.clear()


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


def _register_celery_app_tasks():
    """Register all tasks found in installed plugins."""
    plugin_mgr = extension.ExtensionManager(namespace='excewo.tasks')
    installed_task_plugins = plugin_mgr.list_entry_points()
    logging.info('Found task plugins: {}'.format(
        ', '.join(plugin.name for plugin in installed_task_plugins)
    ))


@contextmanager
def set_up_worker(log_level=None, excewo_config_path=None, app_name=None, celery_app_config=None):
    """Context manager that set up the Celery worker with correct name, config and tasks."""
    with _log_app(log_level), \
            _celery_app_config(excewo_config_path) as config:
        celery_app_name = (app_name or config.get('excewo', 'celery_app_name', fallback=None))
        if celery_app_name:
            logging.info('Setting Celery application name to "{}"'.format(celery_app_name))
            app.main = celery_app_name
        # Set config
        app.add_defaults(DEFAULT_CONFIG)
        # Celery config mess: need to access config before calling app.config_from_object()
        logging.debug('Added default configuration for Celery application {}'.format(
            ', '.join('{}={}'.format(k, app.conf[k]) for k in DEFAULT_CONFIG.keys())
        ))
        celery_app_config = (celery_app_config or
                             config.get('excewo', 'celery_app_config', fallback=None))
        if celery_app_config:
            logging.debug('Reading Celery application configuration from '
                          '{}'.format(celery_app_config))
            app.config_from_object(celery_app_config, force=True)
        for section in config:
            if section not in ('DEFAULT', 'excewo'):
                app.conf[section] = dict(config.items(section=section))
        logging.debug('Final Celery application configuration is: {}'.format(app.conf))
        _register_celery_app_tasks()
        yield


def start_daemon():
    """Start the right daemon, depending on command line argments."""
    cli_args = _command_line_arguments()
    command = cli_args.command
    logging.debug('Launching {}'.format(command))
    if command == 'worker':
        start_worker(cli_args.log_level, cli_args.cli_config_path, cli_args.celery_app_name,
                     cli_args.celery_app_config, cli_args.worker_args[1:])
    elif command == 'flower':
        start_flower(cli_args.log_level, cli_args.cli_config_path, cli_args.celery_app_name,
                     cli_args.celery_app_config)


def start_worker(log_level, excewo_config_path, app_name, celery_app_config, worker_args):
    """Start the Celery worker."""
    with set_up_worker(log_level=log_level, excewo_config_path=excewo_config_path,
                       app_name=app_name, celery_app_config=celery_app_config):
        worker_args = ['excewo'] + worker_args
        if log_level:
            worker_args.extend(['-l', _LOG_LEVEL_MAP[log_level]])
        logging.debug('Running Celery worker with arguments: {}'.format(
            ' '.join(worker_args[1:])
        ))
        app.worker_main(argv=worker_args)


def start_flower(log_level, excewo_config_path, app_name, celery_app_config):
    """Start the flower daemon."""
    with set_up_worker(log_level=log_level, excewo_config_path=excewo_config_path,
                       app_name=app_name, celery_app_config=celery_app_config):
        logging.debug('Running Celery Flower')
        flower = FlowerCommand(app=app)
        flower.execute_from_commandline()


main = start_daemon


if __name__ == '__main__':
    main()
