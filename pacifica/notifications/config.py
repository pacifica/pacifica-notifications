#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
from os import getenv
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import ConfigParser as SafeConfigParser
from pacifica.notifications.globals import CONFIG_FILE


def get_config():
    """Return the ConfigParser object with defaults set."""
    configparser = SafeConfigParser({
        'default_user': getenv(
            'DEFAULT_USER',
            'default_user'
        )
    })
    configparser.add_section('database')
    configparser.set(
        'database',
        'peewee_url',
        getenv(
            'PEEWEE_URL',
            'sqliteext:///db.sqlite3'
        )
    )
    configparser.read(CONFIG_FILE)
    return configparser
