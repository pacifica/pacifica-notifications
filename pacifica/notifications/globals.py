#!/usr/bin/python
"""Global configuration options expressed in environment variables."""
from os import getenv
from os.path import expanduser, join

CONFIG_FILE = getenv('NOTIFICATIONS_CONFIG',  join(expanduser("~"), '.pacifica-notifications', 'config.ini'))
