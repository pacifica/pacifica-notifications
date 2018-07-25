#!/usr/bin/python
"""The ORM module defining the SQL model for notifications."""
import uuid
from datetime import datetime
from jsonpath_rw import parse
from peewee import Model, BooleanField, CharField, TextField, DateTimeField, UUIDField
from playhouse.db_url import connect
from pacifica.notifications.config import get_config

DB = connect(get_config().get('database', 'peewee_url'))

class EventMatch(Model):
    """Events matching via jsonpath per user."""

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    name = CharField(index=True)
    jsonpath = TextField()
    user = CharField(index=True)
    enabled = BooleanField(index=True, default=True)
    error = TextField(null=True)
    created = DateTimeField(default=datetime.now, index=True)
    updated = DateTimeField(default=datetime.now, index=True)
    deleted = DateTimeField(null=True, index=True)

    class Meta:
        database = DB

    def validate_jsonpath(self):
        """Validate the jsonpath string."""
        parse(self.jsonpath)
        return True
