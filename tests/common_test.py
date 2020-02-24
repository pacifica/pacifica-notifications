#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
from time import sleep
import threading
import requests
import cherrypy
from celery.bin.celery import main as celery_main
from pacifica.notifications.orm import EventMatch, EventLogMatch, EventLog, NotificationSystem, DB
from pacifica.notifications.rest import Root, error_page_default
from pacifica.notifications.globals import CHERRYPY_CONFIG


def eventmatch_droptables(func):
    """Setup the database and drop it once done."""
    def wrapper(*args, **kwargs):
        """Create the database table."""
        for orm_obj in [EventLogMatch, EventMatch, EventLog]:
            orm_obj.database_connect()
            if orm_obj.table_exists():
                orm_obj.drop_table()
        for orm_obj in [EventLog, EventMatch, EventLogMatch]:
            orm_obj.create_table()
        func(*args, **kwargs)
        for orm_obj in [EventLogMatch, EventMatch, EventLog]:
            orm_obj.drop_table()
    return wrapper


class NotificationsCPTest:
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
            'target_url': 'http://127.0.0.1:8080',
            'auth': {
                'type': 'basic',
                'basic': {
                    'username': 'dmlb2001',
                    'password': 'password'
                }
            }
        }
        local_data.update(kwargs.get('json_data', {}))
        return requests.post(
            '{}/eventmatch'.format(self.url),
            data=dumps(local_data),
            headers=local_headers
        )

    # pylint: disable=invalid-name
    def setUp(self):
        """Setup the database with in memory sqlite."""
        DB.drop_tables([EventLogMatch, EventLog, EventMatch, NotificationSystem], safe=True)

        def run_celery_worker():
            """Run the main solo worker."""
            return celery_main([
                'celery', '-A', 'pacifica.notifications.tasks', 'worker', '--pool', 'solo',
                '--quiet', '-b', 'redis://127.0.0.1:6379/0'
            ])

        self.celery_thread = threading.Thread(target=run_celery_worker)
        self.celery_thread.start()
        sleep(3)

    # pylint: disable=invalid-name
    def tearDown(self):
        """Tear down the test and remove local state."""
        try:
            celery_main([
                'celery', '-A', 'pacifica.notifications.tasks', 'control',
                '-b', 'redis://127.0.0.1:6379/0', 'shutdown'
            ])
        except SystemExit:
            pass
        self.celery_thread.join()
        try:
            celery_main([
                'celery', '-A', 'pacifica.notifications.tasks', '-b', 'redis://127.0.0.1:6379/0',
                '--force', 'purge'
            ])
        except SystemExit:
            pass
