"""Tests for the Celery application."""


from unittest.mock import patch
import contextlib
import pathlib
import sys
import unittest

from extensible_celery_worker import DEFAULT_CONFIG, app
from extensible_celery_worker.__main__ import main

from celery.contrib.testing.app import DEFAULT_TEST_CONFIG
# This is because there is an "assert tasks.ping in registered_tasks" in celery testing package
from celery.contrib.testing.tasks import ping  # noqa
from celery.contrib.testing.worker import start_worker as _start_worker
import pytest


@pytest.mark.usefixtures('start_worker')
class CeleryAppDefaultInitTest(unittest.TestCase):
    """Test the Celery application default initialization."""

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.add_defaults(DEFAULT_TEST_CONFIG)

    def test_app_name(self):
        """Check that the Celery application name is as expected."""
        self.assertEqual(self.app.main, 'default_extensible_celery_worker_app')

    def test_app_config(self):
        """Check that the Celery application configuration is as expected."""
        for k, v in DEFAULT_TEST_CONFIG.items():
            with self.subTest(msg='Check that Celery application configuration value for key {k} '
                              'is as expected.'.format(k=k)):
                self.assertEqual(self.app.conf[k], v)

    def test_worker_startup_info(self):
        """Check that the Celery worker startup message contains expected strings."""
        startup_msg = self.app.Worker().startup_info()
        for expected_string in ('[config]', 'app:', 'transport:', 'results:', 'concurrency:',
                                'task events:', '[queues]'):
            with self.subTest(msg='Check that Celery worker startup message contains '
                              '"{}".'.format(expected_string)):
                self.assertIn(expected_string, startup_msg)


class CeleryAppCliInitTest(unittest.TestCase):
    """Test the Celery application initialization from excewo script."""

    def setUp(self):
        self.app = app
        self.app.add_defaults(DEFAULT_TEST_CONFIG)
        # Patch app.worker_main() so that a worker is not really started
        patcher = patch.object(app, 'worker_main')
        self.mock_app_worker_main = patcher.start()
        self.addCleanup(patcher.stop)

    def test_app_default_name(self):
        """Check that the Celery application name is default if not set on command line."""
        with patch.object(sys, 'argv', ['excewo']):
            main()
            self.assertEqual(self.app.main, 'default_extensible_celery_worker_app')

    def test_app_set_name_cli(self):
        """Check that the Celery application name is set to the one given on command line."""
        celery_app_name = 'my_worker'
        for cli_option in ('-n', '--app-name'):
            with patch.object(sys, 'argv', ['excewo', cli_option, celery_app_name]), \
                    self.subTest(msg='Check that the Celery application name is set to {} when '
                                 'given with option `{}`.'.format(celery_app_name, cli_option)):
                main()
                self.assertEqual(self.app.main, celery_app_name)

    def test_worker_args(self):
        """Check that the Celery worker is called with arguments given on command line."""
        for worker_args in ([], ['-E'], ['-C', '1', '-E'], ['-E', '--time-limit', '500'],
                            ['-E', '-l', 'INFO']):
            with patch.object(sys, 'argv', ['excewo', '-n', 'my_worker', '--'] + worker_args), \
                    self.subTest(msg='Check that the Celery worker is called with `{}` '
                                 'arguments.'.format(worker_args)):
                main()
                self.mock_app_worker_main.assert_called_with(argv=['excewo'] + worker_args)

    def test_worker_args_with_log_level(self):
        """Check that the log level cli arg is passed to the Celery."""
        with patch.object(sys, 'argv', ['excewo', '-n', 'my_worker', '-l', 'DEBUG', '--', '-E']):
            main()
            self.mock_app_worker_main.assert_called_with(argv=['excewo', '-E', '-l', 'DEBUG'])


class CeleryAppNameTest(unittest.TestCase):
    """Specific test for the Celery application name."""

    def setUp(self):
        self.app = app
        self.app.main = 'default_extensible_celery_worker_app'
        self.app.add_defaults(DEFAULT_TEST_CONFIG)
        # Patch app.worker_main() so that a worker is not really started
        patcher = patch.object(app, 'worker_main')
        self.mock_app_worker_main = patcher.start()
        self.addCleanup(patcher.stop)

    def test_app_default_name(self):
        """Check that the default name is used when no cli arg nor configuration file is given."""
        with patch.object(sys, 'argv', ['excewo']):
            main()
            self.assertEqual(self.app.main, 'default_extensible_celery_worker_app')

    def test_app_name_from_cli(self):
        """Check that the application name is set to what is given by ``-n`` argument."""
        cli_celery_app_name = 'my_worker'
        with patch.object(sys, 'argv', ['excewo', '-n', cli_celery_app_name]):
            main()
            self.assertEqual(self.app.main, cli_celery_app_name)

    def test_app_name_from_config(self):
        """Check that the application name is set to what is given by configuration file."""
        test_config_file_path = pathlib.Path(__file__).parent / 'data' / 'excewo.ini'
        with patch.object(sys, 'argv', ['excewo', '-a', test_config_file_path.as_posix()]):
            main()
            self.assertEqual(self.app.main, 'test_worker')

    def test_app_name_cl_wins(self):
        """Check that the application name is set to what is provided by ``-n`` argument even if
        configuration file is given."""
        cli_celery_app_name = 'my_worker'
        test_config_file_path = pathlib.Path(__file__).parent / 'data' / 'excewo.ini'
        with patch.object(sys, 'argv', ['excewo',
                                        '-n', cli_celery_app_name,
                                        '-a', test_config_file_path.as_posix()]):
            main()
            self.assertEqual(self.app.main, cli_celery_app_name)


class CeleryAppConfigTest(unittest.TestCase):
    """Specific test for the Celery application config."""

    def setUp(self):
        self.app = app
        self.app.main = 'default_extensible_celery_worker_app'
        self.app.conf.update(DEFAULT_CONFIG)
        # Patch app.worker_main() so that a worker is not really started
        patcher = patch.object(app, 'worker_main')
        self.mock_app_worker_main = patcher.start()
        self.addCleanup(patcher.stop)

    def test_app_default_config(self):
        """Check that the default configuration is used when no cli arg nor configuration file is
        given."""
        with patch.object(sys, 'argv', ['excewo']):
            main()
            for k, v in DEFAULT_CONFIG.items():
                self.assertEqual(self.app.conf[k], v)

    def test_app_config_path_from_cli(self):
        """Check that Celery configuration is as expected when ``--config`` argument is given."""
        with patch.object(sys, 'argv', ['excewo', '--config',
                                        'extensible_celery_worker.examples.example2_celeryconfig']):
            main()
            self.assertEqual(self.app.conf['broker_url'], 'amqp://')
            self.assertEqual(self.app.conf['result_backend'], 'redis://')
            self.assertFalse(self.app.conf['task_ignore_result'])
            self.assertTrue(self.app.conf['enable_utc'])
            self.assertEqual(self.app.conf['timezone'], 'UTC')
            self.assertFalse(self.app.conf['worker_send_task_events'])

    def test_app_config_path_from_config_file(self):
        """Check that Celery configuration is as expected when configuration file contains
        ``celery_app_config`` setting."""
        test_config_file_path = pathlib.Path(__file__).parent / 'data' / 'excewo.ini'
        with patch.object(sys, 'argv', ['excewo', '-a', test_config_file_path.as_posix()]):
            main()
            self.assertEqual(self.app.conf['broker_url'],
                             'amqp://excewo:password@rabbitmq.priv.example.org/excewo')
            self.assertIsNone(self.app.conf['result_backend'])
            self.assertTrue(self.app.conf['task_ignore_result'])
            self.assertTrue(self.app.conf['enable_utc'])
            self.assertEqual(self.app.conf['timezone'], 'Europe/Paris')
            self.assertTrue(self.app.conf['worker_send_task_events'])

    def test_app_config_path_from_cli_wins(self):
        """Check that configuration path given by ``--config`` argument takes precedence on
        ``celery_app_config`` setting in ``excewo`` configuration file."""
        test_config_file_path = pathlib.Path(__file__).parent / 'data' / 'excewo.ini'
        with patch.object(sys, 'argv', ['excewo',
                                        '--config',
                                        'extensible_celery_worker.examples.example2_celeryconfig',
                                        '-a', test_config_file_path.as_posix()]):
            main()
            self.assertEqual(self.app.conf['broker_url'], 'amqp://')
            self.assertEqual(self.app.conf['result_backend'], 'redis://')
            self.assertFalse(self.app.conf['task_ignore_result'])
            self.assertTrue(self.app.conf['enable_utc'])
            self.assertEqual(self.app.conf['timezone'], 'UTC')
            self.assertFalse(self.app.conf['worker_send_task_events'])


@pytest.fixture(scope='class')
def start_worker(request):
    with contextlib.ExitStack() as context_managers:
        yield context_managers.enter_context(_start_worker(request.cls.app))
