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
        orm.EventMatch.create_table()
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.config.update('server.conf')
        cherrypy.tree.mount(Root(), '/', 'server.conf')

    @classmethod
    def teardown_class(cls):
        """Destroy tables."""
        super(EventMatchCPTest, cls).teardown_class()
        orm.EventMatch.drop_table()

    def _create_eventmatch(self):
        """Create a test eventmatch and return resp."""
        return requests.post(
            '{}/eventmatch'.format(self.url),
            data=dumps({
                'name': 'testevent',
                'jsonpath': 'foo[*].bar',
                'target_url': 'http://example.com/callback'
            }),
            headers=self.headers
        )

    def test_create(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertTrue('uuid' in resp.json())

    def test_delete(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.delete(
            '{}/eventmatch/{}'.format(self.url, uuid)
        )
        self.assertEqual(resp.status_code, 200)
