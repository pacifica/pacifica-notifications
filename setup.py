#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the pacifica service."""
from os import path
from setuptools import setup, find_packages


setup(
    name='pacifica-notifications',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Pacifica Notifications Service',
    url='https://github.com/pacifica/pacifica-notifications/',
    long_description=open(path.join(
        path.abspath(path.dirname(__file__)),
        'README.md')).read(),
    long_description_content_type='text/markdown',
    author='David Brown',
    author_email='dmlb2000@gmail.com',
    packages=find_packages(include=['pacifica.*']),
    namespace_packages=['pacifica'],
    entry_points={
        'console_scripts': [
            'pacifica-notifications=pacifica.notifications.__main__:main',
            'pacifica-notifications-cmd=pacifica.notifications.__main__:cmd'
        ]
    },
    install_requires=[
        'celery',
        'cherrypy',
        'jsonpath2',
        'jsonschema',
        'pacifica-namespace',
        'peewee',
        'requests'
    ]
)
