"""Tests for the config_paths module."""


from unittest.mock import patch
import os
import pathlib
import platform
import unittest

from extensible_celery_worker.config_paths import config_paths


class ConfigPathsTest(unittest.TestCase):
    """Test for the config_paths function."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._least_expected_paths = [
            pathlib.Path('/') / 'etc' / 'excewo' / 'excewo.ini',
            pathlib.Path(os.environ['HOME']) / '.config' / 'excewo' / 'excewo.ini',
        ]

    def test_config_paths_no_env_no_cli(self):
        """Check that configuration paths are as expected by default."""
        if platform.mac_ver()[0] != '' or platform.win32_ver()[0] != '':
            self.skipTest('Not testing configuration path resolver under Mac OS X or Windows')
        self.assertEqual(list(config_paths()), self._least_expected_paths)

    def test_config_paths_env_no_cli(self):
        """Check that configuration paths are as expected when EXCEWO_CONF env var is set."""
        if platform.mac_ver()[0] != '' or platform.win32_ver()[0] != '':
            self.skipTest('Not testing configuration path resolver under Mac OS X or Windows')
        with patch.dict('os.environ', {'EXCEWO_CONF': '/tmp/excewo.ini'}):
            self.assertEqual(list(config_paths()),
                             self._least_expected_paths + [pathlib.Path(os.environ['EXCEWO_CONF'])])

    def test_config_paths_no_env_cli(self):
        """Check that configuration paths are as expected when cli config path is given."""
        if platform.mac_ver()[0] != '' or platform.win32_ver()[0] != '':
            self.skipTest('Not testing configuration path resolver under Mac OS X or Windows')
        cli_config_path = '/opt/excewo/etc/excewo.ini'
        self.assertEqual(list(config_paths(cli_config_path)),
                         self._least_expected_paths + [pathlib.Path(cli_config_path)])

    def test_config_paths_env_cli(self):
        """Check that configuration paths are as expected when both EXCEWO_CONF env var and cli
        config path are given."""
        if platform.mac_ver()[0] != '' or platform.win32_ver()[0] != '':
            self.skipTest('Not testing configuration path resolver under Mac OS X or Windows')
        cli_config_path = '/opt/excewo/etc/excewo.ini'
        with patch.dict('os.environ', {'EXCEWO_CONF': '/tmp/excewo.ini'}):
            self.assertEqual(list(config_paths(cli_config_path)),
                             self._least_expected_paths +
                             [pathlib.Path(os.environ['EXCEWO_CONF']),
                              pathlib.Path(cli_config_path)])

    def test_config_paths_empty_cli(self):
        """Check that configuration paths do not consider cli config path if empty or ``None``."""
        if platform.mac_ver()[0] != '' or platform.win32_ver()[0] != '':
            self.skipTest('Not testing configuration path resolver under Mac OS X or Windows')
        for cli_config_path in ('', None):
            with self.subTest(msg='Check that configuration paths do not consider cli config path '
                              'if equals to `{}`'.format(cli_config_path)):
                self.assertEqual(list(config_paths(cli_config_path)), self._least_expected_paths)
