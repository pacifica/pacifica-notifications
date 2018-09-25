#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The ORM module defining the SQL model for notifications."""
import uuid
from time import sleep
from datetime import datetime
from json import loads
from peewee import Model, CharField, TextField, DateTimeField, UUIDField, OperationalError
from playhouse.db_url import connect
from pacifica.notifications.config import get_config
from pacifica.notifications.jsonpath import parse

DATABASE_CONNECT_ATTEMPTS = 20
DATABASE_WAIT = 5
DB = connect(get_config().get('database', 'peewee_url'))


def database_setup(attempts=0):
    """Setup the database."""
    try:
        EventMatch.connect()
        EventMatch.database_setup()
        EventMatch.close()
    except OperationalError:
        if attempts < DATABASE_CONNECT_ATTEMPTS:
            sleep(DATABASE_WAIT)
            attempts += 1
            database_setup(attempts)
        else:
            raise OperationalError


class EventMatch(Model):
    """Events matching via jsonpath per user."""

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    name = CharField(index=True)
    jsonpath = TextField()
    user = CharField(index=True)
    disabled = DateTimeField(index=True, null=True, default=None)
    error = TextField(null=True)
    target_url = TextField()
    version = CharField(default='v0.1')
    # JSONField is extension specific and we are using URLs to bind
    # to a database backend
    extensions = TextField(default='{}')
    created = DateTimeField(default=datetime.now, index=True)
    updated = DateTimeField(default=datetime.now, index=True)
    deleted = DateTimeField(null=True, index=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """The meta class that contains db connection."""

        database = DB
    # pylint: enable=too-few-public-methods

    def validate_jsonpath(self):
        """Validate the jsonpath string."""
        parse(self.jsonpath)
        return True

    @classmethod
    def database_setup(cls):
        """Setup the database by creating all tables."""
        if not cls.table_exists():
            cls.create_table()

    @classmethod
    def connect(cls):
        """Connect to the database."""
        cls._meta.database.connect(True)

    @classmethod
    def close(cls):
        """Close the connection to the database."""
        cls._meta.database.close()

    @classmethod
    def atomic(cls):
        """Do the database atomic action."""
        return cls._meta.database.atomic()

    def to_hash(self):
        """Convert the object to a json serializable hash."""
        ret_obj = {}
        for field_name in self._meta.sorted_field_names:
            ret_obj[field_name] = getattr(self, field_name)
        ret_obj['uuid'] = str(ret_obj['uuid'])
        ret_obj['extensions'] = loads(ret_obj['extensions'])
        for dt_element in ['disabled', 'deleted', 'updated', 'created']:
            if getattr(self, dt_element):
                # pylint: disable=no-member
                ret_obj[dt_element] = getattr(self, dt_element).isoformat()
                # pylint: enable=no-member
        return ret_obj
