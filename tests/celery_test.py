#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from os.path import join
from datetime import datetime
from time import sleep
from json import loads, dumps
import requests
from pacifica.notifications.orm import EventMatch
from common_test import NotificationsCPTest, eventmatch_droptables


class CeleryCPTest(NotificationsCPTest):
    """Test the EventMatch class."""

    @eventmatch_droptables
    def test_bad_url(self):
        """Test the create POST method in EventMatch."""
        uuid_list = []
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'doesnotexist'}
        )
        eventmatch_obj = resp.json()
        self.assertEqual(eventmatch_obj['user'], 'doesnotexist')
        uuid_list.append(eventmatch_obj['uuid'])
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'bjohn'}
        )
        eventmatch_obj = resp.json()
        self.assertEqual(eventmatch_obj['user'], 'bjohn')
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'dmlb2001'},
            json_data={'target_url': 'http://127.0.0.1:8080/something/no/where'}
        )
        eventmatch_obj = resp.json()
        self.assertEqual(eventmatch_obj['user'], 'dmlb2001')
        self.assertEqual(
            eventmatch_obj['target_url'], 'http://127.0.0.1:8080/something/no/where'
        )
        uuid_list.append(eventmatch_obj['uuid'])
        event_obj = loads(open(join('test_files', 'events.json')).read())
        resp = requests.post(
            '{}/receive'.format(self.url),
            data=dumps(event_obj),
            headers={'Content-Type': 'application/cloudevents+json; charset=utf-8'}
        )
        self.assertEqual(resp.status_code, 200)
        sleep(10)
        for uuid in uuid_list:
            eventmatch_obj = EventMatch.get(EventMatch.uuid == uuid)
            self.assertEqual(eventmatch_obj.disabled.year, datetime.now().year)

    @eventmatch_droptables
    def test_bad_connection(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'dmlb2001'},
            json_data={'target_url': 'http://127.0.0.1:8192/something/no/where'}
        )
        eventmatch_obj = resp.json()
        self.assertEqual(eventmatch_obj['user'], 'dmlb2001')
        self.assertEqual(
            eventmatch_obj['target_url'], 'http://127.0.0.1:8192/something/no/where'
        )
        event_obj = loads(open(join('test_files', 'events.json')).read())
        resp = requests.post(
            '{}/receive'.format(self.url),
            data=dumps(event_obj),
            headers={'Content-Type': 'application/cloudevents+json; charset=utf-8'}
        )
        self.assertEqual(resp.status_code, 200)
        sleep(10)
        EventMatch.connect()
        eventmatch_obj = EventMatch.get(
            EventMatch.uuid == eventmatch_obj['uuid']
        )
        EventMatch.close()
        self.assertEqual(eventmatch_obj.disabled.year, datetime.now().year)

    @eventmatch_droptables
    def test_create(self):
        """Test the create POST method in EventMatch."""
        resp = self._create_eventmatch(
            headers={'Http-Remote-User': 'dmlb2001'}
        )
        eventmatch_obj = resp.json()
        self.assertEqual(eventmatch_obj['user'], 'dmlb2001')
        event_obj = loads(open(join('test_files', 'events.json')).read())
        resp = requests.post(
            '{}/receive'.format(self.url),
            data=dumps(event_obj),
            headers={'Content-Type': 'application/cloudevents+json; charset=utf-8'}
        )
        self.assertEqual(resp.status_code, 200)
        sleep(10)
        EventMatch.connect()
        eventmatch_obj = EventMatch.get(
            EventMatch.uuid == eventmatch_obj['uuid']
        )
        EventMatch.close()
        self.assertEqual(eventmatch_obj.disabled, None)
