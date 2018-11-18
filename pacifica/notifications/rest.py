#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy module containing classes for rest interface."""
from uuid import UUID
from datetime import datetime
from json import dumps, loads
from jsonschema import validate
import cherrypy
from cherrypy import HTTPError
from peewee import DoesNotExist
from six import PY2
from pacifica.notifications import orm
from pacifica.notifications.config import get_config
from pacifica.notifications.tasks import dispatch_event


def encode_text(thing_obj):
    """Encode the text to bytes."""
    if PY2:  # pragma: no cover only for python 2
        return str(thing_obj)
    return bytes(thing_obj, 'utf8')  # pragma: no cover only for python 3


def get_remote_user():
    """Get the remote user from cherrypy request headers."""
    return cherrypy.request.headers.get(
        'Http-Remote-User',
        get_config().get('DEFAULT', 'default_user')
    )


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    cherrypy.response.headers['Content-Type'] = 'application/json'
    return dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })


class EventMatch(object):
    """CherryPy EventMatch endpoint."""

    exposed = True
    json_schema = {
        'definitions': {
            'eventmatch': {
                'type': 'object',
                'properties': {
                    'uuid': {'type': 'string'},
                    'name': {'type': 'string'},
                    'jsonpath': {'type': 'string'},
                    'user': {'type': 'string'},
                    'disabled': {'type': ['string', 'null'], 'format': 'date-time'},
                    'error': {'type': ['string', 'null']},
                    'target_url': {'type': 'string'},
                    'version': {'type': 'string'},
                    'extensions': {'type': 'object'},
                    'created': {'type': 'string', 'format': 'date-time'},
                    'updated': {'type': 'string', 'format': 'date-time'},
                    'deleted': {'type': ['string', 'null'], 'format': 'date-time'}
                }
            }
        },
        '$ref': '#/definitions/eventmatch',
        'not': {
            'required': ['uuid', 'user', 'created', 'updated', 'deleted', 'version']
        }
    }

    @staticmethod
    def _http_get(event_uuid):
        """Internal get event by UUID and return peewee obj."""
        cherrypy.response.headers['Content-Type'] = 'application/json'
        orm.EventMatch.connect()
        try:
            event_obj = orm.EventMatch.get(
                orm.EventMatch.uuid == UUID('{{{}}}'.format(event_uuid)))
        except DoesNotExist:
            orm.EventMatch.close()
            raise HTTPError(403, 'Forbidden')
        orm.EventMatch.close()
        if event_obj.user != get_remote_user() or event_obj.deleted:
            raise HTTPError(403, 'Forbidden')
        return event_obj

    @classmethod
    # pylint: disable=invalid-name
    def GET(cls, event_uuid=None):
        """Get the event ID and return it."""
        if event_uuid:
            objs = cls._http_get(event_uuid).to_hash()
        else:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            orm.EventMatch.connect()
            query = orm.EventMatch.select().where(
                (orm.EventMatch.user == get_remote_user()) &
                (orm.EventMatch.deleted >> None)
            )
            objs = [x.to_hash() for x in query]
            orm.EventMatch.close()
        if objs:
            return encode_text(dumps(objs))
        raise HTTPError(403, 'Forbidden')

    @classmethod
    # pylint: disable=invalid-name
    def PUT(cls, event_uuid):
        """Update an Event Match obj in the database."""
        event_obj = cls._http_get(event_uuid)
        json_obj = loads(cherrypy.request.body.read().decode('utf8'))
        validate(json_obj, cls.json_schema)
        json_obj['extensions'] = dumps(json_obj.get('extensions', {}))
        for key, value in json_obj.items():
            setattr(event_obj, key, value)
        event_obj.updated = datetime.now()
        event_obj.validate_jsonpath()
        orm.EventMatch.connect()
        with orm.EventMatch.atomic():
            event_obj.save()
        orm.EventMatch.close()
        return cls.GET(str(event_obj.uuid))

    @classmethod
    # pylint: disable=invalid-name
    def POST(cls):
        """Create an Event Match obj in the database."""
        orm.EventMatch.connect()
        event_match_obj = loads(cherrypy.request.body.read().decode('utf8'))
        validate(event_match_obj, cls.json_schema)
        event_match_obj['extensions'] = dumps(
            event_match_obj.get('extensions', {})
        )
        event_match_obj['user'] = get_remote_user()
        event_obj = orm.EventMatch(**event_match_obj)
        event_obj.validate_jsonpath()
        with orm.EventMatch.atomic():
            event_obj.save(force_insert=True)
        orm.EventMatch.close()
        return cls.GET(str(event_obj.uuid))

    @classmethod
    # pylint: disable=invalid-name
    def DELETE(cls, event_uuid):
        """Delete the event by uuid."""
        event_obj = cls._http_get(event_uuid)
        orm.EventMatch.connect()
        event_obj.deleted = datetime.now()
        event_obj.updated = datetime.now()
        with orm.EventMatch.atomic():
            event_obj.save()
        orm.EventMatch.close()


# pylint: disable=too-few-public-methods
class ReceiveEvent(object):
    """CherryPy Receive Event object."""

    exposed = True
    event_json_schema = {}

    @classmethod
    # pylint: disable=invalid-name
    def POST(cls):
        """Receive the event and dispatch it to backend."""
        event_obj = loads(cherrypy.request.body.read().decode('utf8'))
        validate(event_obj, cls.event_json_schema)
        return encode_text(str(dispatch_event.delay(event_obj)))
# pylint: enable=too-few-public-methods


# pylint: disable=too-few-public-methods
class Root(object):
    """CherryPy Root Object."""

    exposed = True
    eventmatch = EventMatch()
    receive = ReceiveEvent()
# pylint: enable=too-few-public-methods
