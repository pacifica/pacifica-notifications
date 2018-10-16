#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv(
    'NOTIFICATIONS_CONFIG',
    join(
        expanduser('~'),
        '.pacifica-notifications',
        'config.ini'
    )
)
CHERRYPY_CONFIG = getenv(
    'NOTIFICATIONS_CPCONFIG',
    join(
        expanduser('~'),
        '.pacifica-notifications',
        'cpconfig.ini'
    )
)
