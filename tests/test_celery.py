"""Tests for the Celery application."""


import contextlib
import unittest

from extensible_celery_worker import app

from celery.contrib.testing.app import DEFAULT_TEST_CONFIG
# This is because there is an "assert tasks.ping in registered_tasks" in celery testing package
from celery.contrib.testing.tasks import ping  # noqa
from celery.contrib.testing.worker import start_worker as _start_worker
import pytest


@pytest.mark.usefixtures('start_worker')
class CeleryAppInitTest(unittest.TestCase):
    """Test the Celery application initialization."""

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
            with self.subTest(msg=f'Check that Celery application configuration value for key {k} '
                              'is as expected.'):
                self.assertEqual(self.app.conf[k], v)

    def test_worker_startup_info(self):
        """Check that the Celery worker startup message contains expected strings."""
        startup_msg = self.app.Worker().startup_info()
        for expected_string in ('[config]', 'app:', 'transport:', 'results:', 'concurrency:',
                                'task events:', '[queues]'):
            with self.subTest(msg='Check that Celery worker startup message contains '
                              '"{}".'.format(expected_string)):
                self.assertIn(expected_string, startup_msg)


@pytest.fixture(scope='class')
def start_worker(request):
    with contextlib.ExitStack() as context_managers:
        yield context_managers.enter_context(_start_worker(request.cls.app))
