#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the pacifica service."""
from os import path
try:  # pip version 9
    from pip.req import parse_requirements
except ImportError:
    from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt', session='hack')

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
            'pacifica-notifications=pacifica.notifications.__main__:main',
            'pacifica-notifications-cmd=pacifica.notifications.__main__:cmd'
        ]
    },
    install_requires=[str(ir.req) for ir in INSTALL_REQS],
    extras_require={
        ':python_version=="2.7"': [
            'jsonpath-ng'
        ],
        ':python_version>="3.0"': [
            'jsonpath2'
        ]
    }
)
