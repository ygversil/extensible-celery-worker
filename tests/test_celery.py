"""Tests for the Celery application."""


from unittest.mock import patch
import contextlib
import sys
import unittest

from extensible_celery_worker import app
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
        self.app_worker_main = patcher.start()
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


@pytest.fixture(scope='class')
def start_worker(request):
    with contextlib.ExitStack() as context_managers:
        yield context_managers.enter_context(_start_worker(request.cls.app))
