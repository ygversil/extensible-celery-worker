"""Function to yield each path to possible configuration files, depending on the platform.

Inspired by and simplified from https://github.com/barry-scott/config-path.
"""


__all__ = ('config_paths')


import os
import pathlib
import platform

if platform.win32_ver()[0] != '':
    import ctypes
    import ctypes.wintypes


_WORKER_NAME = 'excewo'
_CONF_FILENAME = '{worker_name}.ini'.format(worker_name=_WORKER_NAME)


def _mac_global_config_paths():
    """Yield each path to a global configuration files on Mac OS X platforms."""
    return iter(())


def _mac_home_config_paths():
    """Yield each path to user's configuration files on Mac OS X platforms."""
    yield (pathlib.Path(os.environ['HOME']) / 'Library' / 'Preferences' /
           'org.ygversil.{worker_name}'.format(worker_name=_WORKER_NAME) / _CONF_FILENAME)


def _xdg_global_config_paths():
    """Yield each path to a global configuration files on XDG compatible platforms."""
    for folder_path in os.environ.get('XDG_CONFIG_DIRS', '/etc').split(':'):
        yield pathlib.Path(folder_path) / _WORKER_NAME / _CONF_FILENAME


def _xdg_home_config_paths():
    """Yield each path to user's configuration files on XDG compatible platforms."""
    yield (pathlib.Path(os.environ.get('XDG_CONFIG_HOME',
                                       pathlib.Path(os.environ['HOME']) / '.config')) /
           _WORKER_NAME / _CONF_FILENAME)


def _win_global_config_paths():
    """Yield each path to a global configuration files on Windows platforms."""
    return iter(())


def _win_home_config_paths():
    """Yield each path to user's configuration files on Windows platforms."""
    csidl_appdata = 0x1a  # application data
    shgfp_type_current = 0  # want current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(0, csidl_appdata, 0, shgfp_type_current, buf)
    yield pathlib.Path(buf.value) / _WORKER_NAME / _CONF_FILENAME


def _global_config_paths():
    """Yield each path to a global configuration files."""
    if platform.mac_ver()[0] != '':
        yield from _mac_global_config_paths()
    elif platform.win32_ver()[0] != '':
        yield from _win_global_config_paths()
    else:
        yield from _xdg_global_config_paths()


def _home_config_paths():
    """Yield each path to user's configuration files."""
    if platform.mac_ver()[0] != '':
        yield from _mac_home_config_paths()
    elif platform.win32_ver()[0] != '':
        yield from _win_home_config_paths()
    else:
        yield from _xdg_home_config_paths()


def config_paths(cli_config_path=None):
    """Yield each path to possible configuration files."""
    yield from _global_config_paths()
    yield from _home_config_paths()
    env_config_path = os.environ.get('EXCEWO_CONF')
    if env_config_path:
        yield pathlib.Path(env_config_path)
    if cli_config_path:
        yield pathlib.Path(cli_config_path)
