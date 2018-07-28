#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.notifications.rest import orm, Root, error_page_default


def eventmatch_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        orm.EventMatch.create_table()
        func(*args, **kwargs)
        orm.EventMatch.drop_table()
    return wrapper


class EventMatchCPTest(helper.CPWebCase):
    """Test the EventMatch class."""

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
                'target_url': 'http://example.com/callback'
            }),
            headers=self.headers
        )

    @eventmatch_droptables
    def test_create(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertTrue('uuid' in resp.json())

    @eventmatch_droptables
    def test_delete(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.delete(
            '{}/eventmatch/{}'.format(self.url, uuid)
        )
        self.assertEqual(resp.status_code, 200)

    @eventmatch_droptables
    def test_get_single(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.get(
            '{}/eventmatch/{}'.format(self.url, uuid)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['uuid'], uuid)

    @eventmatch_droptables
    def test_get_list(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.get(
            '{}/eventmatch'.format(self.url)
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()[0]['uuid'], uuid)

    @eventmatch_droptables
    def test_update(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.put(
            '{}/eventmatch/{}'.format(self.url, uuid),
            data=dumps({
                'target_url': 'http://example.com/1234'
            }),
            headers=self.headers
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['uuid'], uuid)
        self.assertEqual(resp.json()['target_url'], 'http://example.com/1234')
