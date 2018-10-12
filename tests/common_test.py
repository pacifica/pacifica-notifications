#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.notifications.orm import database_setup, EventMatch
from pacifica.notifications.rest import Root, error_page_default
from pacifica.notifications.globals import CHERRYPY_CONFIG


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
        cherrypy.config.update(CHERRYPY_CONFIG)
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)

    def _create_eventmatch(self, **kwargs):
        """Create a test eventmatch and return resp."""
        local_headers = kwargs.get('headers', {})
        local_headers.update(self.headers)
        local_data = {
            'name': 'testevent',
            'jsonpath': '$.data[?(@.value="Blah")].value',
            'target_url': 'http://127.0.0.1:8080'
        }
        local_data.update(kwargs.get('json_data', {}))
        return requests.post(
            '{}/eventmatch'.format(self.url),
            data=dumps(local_data),
            headers=local_headers
        )
