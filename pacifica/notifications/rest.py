#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy module containing classes for rest interface."""
from uuid import UUID
from json import dumps, loads
import cherrypy
from cherrypy import HTTPError, tools
from pacifica.notifications import orm
from pacifica.notifications.config import get_config


def get_remote_user():
    """Get the remote user from cherrypy request headers."""
    return cherrypy.request.headers.get('Http-Remote-User', get_config().get('DEFAULT', 'default_user'))


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

    @staticmethod
    # pylint: disable=invalid-name
    def GET(event_uuid=None):
        """Get the event ID and return it."""
        orm.EventMatch.connect()
        if event_uuid:
            query = orm.EventMatch.uuid == UUID('{{{}}}'.format(event_uuid))
        else:
            query = orm.EventMatch.user == get_remote_user()
        # peewee does dynamic kwargs style of select statements.
        # pylint: disable=unexpected-keyword-arg
        objs = [x.to_hash() for x in orm.EventMatch.select().where(query)]
        orm.EventMatch.close()
        if objs:
            if event_uuid:
                return bytes(dumps(objs[0]), 'utf8')
            return bytes(dumps(objs), 'utf8')
        raise HTTPError(404, 'Not Found')

    @tools.json_in()
    @staticmethod
    # pylint: disable=invalid-name
    def POST():
        """Create an Event Match obj in the database."""
        orm.EventMatch.connect()
        event_match_obj = loads(cherrypy.request.body.read().decode('utf8'))
        event_match_obj['user'] = get_remote_user()
        with orm.EventMatch.atomic():
            event_obj = orm.EventMatch(**event_match_obj)
            event_obj.save(force_insert=True)
        orm.EventMatch.close()
        return EventMatch.GET(event_obj.uuid)

    @staticmethod
    # pylint: disable=invalid-name
    def DELETE(event_uuid):
        """Delete the event by uuid."""
        # peewee does dynamic kwargs style of select statements.
        # pylint: disable=unexpected-keyword-arg
        orm.EventMatch.connect()
        objs = orm.EventMatch().select().where(
            orm.EventMatch.uuid == UUID('{{{}}}'.format(event_uuid)))
        if objs:
            if objs[0].user == get_remote_user():
                objs[0].delete_instance()
                orm.EventMatch.close()
                return
            else:
                raise HTTPError(401, 'Unauthorized')
        raise HTTPError(404, 'Not Found')


# pylint: disable=too-few-public-methods
class Root(object):
    """CherryPy Root Object."""

    exposed = True
    eventmatch = EventMatch()
# pylint: enable=too-few-public-methods
