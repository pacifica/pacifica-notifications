#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the pacifica service."""
from os import path
try:  # pip version 9
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements
from setuptools import setup, find_packages
from six import PY2

# parse_requirements() returns generator of pip.req.InstallRequirement objects
REQ_FILE = 'requirements2.txt' if PY2 else 'requirements.txt'
INSTALL_REQS = parse_requirements(REQ_FILE, session='hack')

setup(
    name='pacifica-notifications',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Notifications Service',
    url='https://pypi.python.org/pypi/pacifica-notifications/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='dmlb2000@gmail.com',
    packages=find_packages(),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-notifications=pacifica.notifications.__main__:main'
        ]
    },
    install_requires=[str(ir.req) for ir in INSTALL_REQS]
)
