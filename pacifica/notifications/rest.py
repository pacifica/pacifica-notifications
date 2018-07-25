#!/usr/bin/python
# -*- coding: utf-8 -*-
"""CherryPy module containing classes for rest interface."""
from json import dumps
# pylint: disable=no-name-in-module
from cherrypy import HttpError, expose, tools, request, response
# pylint: enable=no-name-in-module
from pacifica.notifications import orm
from pacifica.notifications.config import get_config


def get_remote_user():
    """Get the remote user from cherrypy request headers."""
    return request.headers.get('Http-Remote-User', get_config().get('DEFAULT', 'default_user'))


def error_page_default(**kwargs):
    """The default error page should always enforce json."""
    response.headers['Content-Type'] = 'application/json'
    return dumps({
        'status': kwargs['status'],
        'message': kwargs['message'],
        'traceback': kwargs['traceback'],
        'version': kwargs['version']
    })


class EventMatch(object):
    """CherryPy EventMatch endpoint."""

    @expose
    @tools.json_out()
    @staticmethod
    # pylint: disable=invalid-name
    def GET(event_uuid=None):
        """Get the event ID and return it."""
        if event_uuid:
            query = {'uuid': event_uuid}
        else:
            query = {'username': get_remote_user()}
        # peewee does dynamic kwargs style of select statements.
        # pylint: disable=unexpected-keyword-arg
        objs = [x for x in orm.EventMatch.select(**query).dicts()]
        if objs:
            return objs[0]
        raise HttpError(404, 'Not Found')

    @expose
    @tools.json_out()
    @tools.json_in()
    @staticmethod
    # pylint: disable=invalid-name
    def POST(event_match_obj):
        """Create an Event Match obj in the database."""
        event_match_obj['username'] = get_remote_user()
        event_obj = orm.EventMatch(**event_match_obj).save()
        return EventMatch.GET(event_obj.uuid)

    @expose
    @staticmethod
    # pylint: disable=invalid-name
    def DELETE(event_uuid):
        """Delete the event by uuid."""
        # peewee does dynamic kwargs style of select statements.
        # pylint: disable=unexpected-keyword-arg
        objs = orm.EventMatch().select(uuid=event_uuid)
        if objs:
            if objs[0].username == get_remote_user():
                objs[0].delete_instance()
            else:
                raise HttpError(401, 'Unauthorized')
        raise HttpError(404, 'Not Found')


# pylint: disable=too-few-public-methods
class Root(object):
    """CherryPy Root Object."""

    eventmatch = EventMatch()
# pylint: enable=too-few-public-methods
