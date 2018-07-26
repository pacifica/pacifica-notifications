#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the example module."""
from json import dumps
import cherrypy
from cherrypy.test import helper
from peewee import SqliteDatabase
from pacifica.notifications.rest import orm, Root, error_page_default


class EventMatchCPTest(helper.CPWebCase):
    """Test the EventMatch class."""

    @classmethod
    def setup_class(cls):
        """Setup the class database."""
        super(EventMatchCPTest, cls).setup_class()
        cls._test_db = SqliteDatabase(':memory:')
        orm.EventMatch.bind(cls._test_db)

    @staticmethod
    def setup_server():
        """Bind tables to in memory db and start service."""
        orm.EventMatch.create_table()
        cherrypy.config.update({'error_page.default': error_page_default})
        cherrypy.tree.mount(Root())

    @classmethod
    def teardown_class(cls):
        """Destroy tables."""
        super(EventMatchCPTest, cls).teardown_class()
        cls._test_db.drop_tables([orm.EventMatch])
        cls._test_db.close()
        cls._test_db = None

    def test_create(self):
        """Test the add method in example class."""
        self.getPage(
            '/eventmatch',
            method='POST',
            body=dumps({
                'name': 'testevent',
                'jsonpath': 'foo[*].bar'
            })
        )
        self.assertStatus('200 OK')
        self.assertHeader('Content-Type', 'application/json')
