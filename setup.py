import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="extensible_celery_worker",
    version="0.2.1",
    url="https://github.com/ygversil/extensible-celery-worker",
    license='MIT',

    author="Yann Voté",
    author_email="ygversil@lilo.org",

    description="Python Celery worker whose registered task list can be extended with plugins",
    long_description=read("README.rst"),
    long_description_content_type='text/x-rst',

    packages=find_packages(exclude=('tests',)),

    python_requires='>=3.6',

    install_requires=[
        'celery<5.0',
        'stevedore',
    ],
    extra_require={
        'flower': [
            'flower',
        ],
    },

    data_files=[
        ('examples', ['excewo.ini.example'])
    ],

    entry_points={
        'console_scripts': [
            'excewo = extensible_celery_worker.__main__:main',
            'excewo-flower = extensible_celery_worker.flower:main',
        ],
        'excewo.tasks': [
            'examples = extensible_celery_worker.examples.tasks',
        ],
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
