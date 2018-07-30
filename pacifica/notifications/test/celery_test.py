#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from os.path import join
from time import sleep
from json import loads, dumps
import requests
from pacifica.notifications.orm import EventMatch
from pacifica.notifications.test.common import NotificationsCPTest, eventmatch_droptables


class CeleryCPTest(NotificationsCPTest):
    """Test the EventMatch class."""

    @eventmatch_droptables
    def test_create(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch(
            headers={'http-remote-user': 'dmlb2001'})
        eventmatch_obj = resp.json()
        event_obj = loads(open(join('test_files', 'events.json')).read())
        resp = requests.post(
            '{}/receive'.format(self.url),
            data=dumps(event_obj),
            headers={'Content-Type': 'application/cloudevents+json; charset=utf-8'}
        )
        self.assertEqual(resp.status_code, 200)
        sleep(20)
        eventmatch_obj = EventMatch.get(
            EventMatch.uuid == eventmatch_obj['uuid'])
        self.assertEqual(eventmatch_obj.disabled, None)
