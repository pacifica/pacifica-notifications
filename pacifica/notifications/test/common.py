#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.notifications.tasks import CELERY_APP
from pacifica.notifications.orm import database_setup, EventMatch
from pacifica.notifications.rest import Root, error_page_default

CELERY_APP.conf.CELERY_ALWAYS_EAGER = True


def eventmatch_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        database_setup()
        func(*args, **kwargs)
        EventMatch.drop_table()
    return wrapper


class NotificationsCPTest(helper.CPWebCase):
    """Base class for all testing classes."""

    HOST = '127.0.0.1'
    PORT = 8070
    url = 'http://{0}:{1}'.format(HOST, PORT)
    headers = {'content-type': 'application/json'}

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update('server.conf')
        cherrypy.tree.mount(Root(), '/', 'server.conf')

    def _create_eventmatch(self):
        """Create a test eventmatch and return resp."""
        return requests.post(
            '{}/eventmatch'.format(self.url),
            data=dumps({
                'name': 'testevent',
                'jsonpath': 'foo[*].bar',
                'target_url': 'http://127.0.0.1:8080'
            }),
            headers=self.headers
        )