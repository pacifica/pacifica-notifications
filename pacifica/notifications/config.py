#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Configuration reading and validation module."""
try:
    from ConfigParser import SafeConfigParser
except ImportError:  # pragma: no cover python 2 vs 3 issue
    from configparser import SafeConfigParser
from pacifica.notifications.globals import CONFIG_FILE


def get_config():
    """Return the ConfigParser object with defaults set."""
    configparser = SafeConfigParser({
        'peewee_url': 'sqliteext:///db.sqlite3',
        'default_user': 'default_user'
    })
    configparser.add_section('database')
    configparser.read(CONFIG_FILE)
    return configparser
