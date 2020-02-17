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
    configparser.add_section('celery')
    configparser.set('celery', 'broker_url', getenv(
        'BROKER_URL', 'redis://localhost:6379/0'))
    configparser.set('celery', 'backend_url', getenv(
        'BACKEND_URL', 'rpc://'))
    configparser.add_section('notifications')
    configparser.set('notifications', 'user_header', getenv(
        'USER_HEADER', 'Http-Remote-User'))
    configparser.set('notifications', 'policy_url', getenv(
        'POLICY_URL', 'http://localhost:8181'))
    configparser.add_section('database')
    configparser.set('database', 'peewee_url', getenv(
        'PEEWEE_URL', 'postgres://notifications:notifications@localhost/pacifica_notifications'))
    configparser.set('database', 'connect_attempts', getenv(
        'DATABASE_CONNECT_ATTEMPTS', '10'))
    configparser.set('database', 'connect_wait', getenv(
        'DATABASE_CONNECT_WAIT', '20'))
    configparser.read(CONFIG_FILE)
    return configparser
