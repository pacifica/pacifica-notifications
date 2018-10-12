#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import requests
from common_test import NotificationsCPTest, eventmatch_droptables


class EventMatchCPTest(NotificationsCPTest):
    """Test the EventMatch class."""

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
    def test_setting_alternate_user(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'dmlb2001'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['user'], 'dmlb2001')

    @eventmatch_droptables
    def test_update_wrong_user(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch()
        resp = requests.put(
            '{}/eventmatch/{}'.format(self.url, resp.json()['uuid']),
            data=dumps({
                'target_url': 'http://foo.example.com/1234'
            }),
            headers={
                'Http-Remote-User': 'dmlb2001',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['status'], '403 Forbidden')

    @eventmatch_droptables
    def test_delete_wrong_user(self):
        """Test the delete method in EventMatch."""
        resp = self._create_eventmatch()
        uuid = resp.json()['uuid']
        resp = requests.delete(
            '{}/eventmatch/{}'.format(self.url, uuid),
            headers={
                'Http-Remote-User': 'dmlb2001',
                'Content-Type': 'application/json'
            }
        )
        self.assertEqual(resp.status_code, 403)
        self.assertTrue('Content-Type' in resp.headers)
        self.assertEqual(resp.headers['Content-Type'], 'application/json')
        self.assertEqual(resp.json()['status'], '403 Forbidden')
