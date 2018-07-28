#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
import cherrypy
from cherrypy.test import helper
from pacifica.notifications.orm import database_setup, EventMatch
from pacifica.notifications.rest import Root, error_page_default


def eventmatch_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        database_setup()
        func(*args, **kwargs)
        EventMatch.drop_table()
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

    @eventmatch_droptables
    def test_not_found(self):
        """Test the delete method in EventMatch."""
        for uuid in ['', '6cf47199-5abf-4ae3-a40d-9d6283d0ee21']:
            resp = requests.get('{}/eventmatch/{}'.format(self.url, uuid))
            self.assertEqual(resp.status_code, 403)
            self.assertTrue('Content-Type' in resp.headers)
            self.assertEqual(resp.headers['Content-Type'], 'application/json')
            self.assertEqual(resp.json()['status'], '403 Forbidden')

    @eventmatch_droptables
    def test_bad_uuid(self):
        """Test the get with bad UUID."""
        resp = requests.get(
            '{}/eventmatch/1234'.format(self.url)
        )
        self.assertEqual(resp.status_code, 500)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['status'], '500 Internal Server Error')

    @eventmatch_droptables
    def test_get_wrong_user(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch()
        resp = requests.get(
            '{}/eventmatch/{}'.format(self.url, resp.json()['uuid']),
            headers={'Http-Remote-User': 'dmlb2001'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['status'], '403 Forbidden')

    @eventmatch_droptables
    def test_update_wrong_user(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch()
        resp = requests.put(
            '{}/eventmatch/{}'.format(self.url, resp.json()['uuid']),
            data=dumps({
                'target_url': 'http://foo.example.com/1234'
            }),
            headers={'Http-Remote-User': 'dmlb2001'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['status'], '403 Forbidden')
