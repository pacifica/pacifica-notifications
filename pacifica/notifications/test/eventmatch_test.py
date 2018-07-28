#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.notifications.rest import orm, Root, error_page_default


class EventMatchCPTest(helper.CPWebCase):
    """Test the EventMatch class."""

    HOST = '127.0.0.1'
    PORT = 8070
    url = 'http://{0}:{1}'.format(HOST, PORT)
    headers = {'content-type': 'application/json'}

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        print('Entering setup_server().')
        orm.EventMatch.create_table()
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update('server.conf')
        cherrypy.tree.mount(Root(), '/', 'server.conf')
        print('Finished setup_server().')

    @classmethod
    def teardown_class(cls):
        """Destroy tables."""
        print('Entering teardown_class().')
        super(EventMatchCPTest, cls).teardown_class()
        orm.EventMatch.drop_table()
        print('Finished teardown_class().')

    def test_create(self):
        """Test the create POST method in EventMatch."""
        resp = requests.post(
            '{}/eventmatch'.format(self.url),
            data=dumps({
                'name': 'testevent',
                'jsonpath': 'foo[*].bar',
                'target_url': 'http://example.com/callback'
            }),
            headers=self.headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
