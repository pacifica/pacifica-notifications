#!/usr/bin/python
"""CherryPy module containing classes for rest interface."""
import cherrypy
from pacifica.notifications import orm
from pacifica.notifications.globals import get_config


def get_remote_user():
    """Get the remote user from cherrypy request headers."""
    return cherrypy.request.headers.get('Http-Remote-User', get_config.get('DEFAULT', 'default_user'))

class EventMatch(object):
    """CherryPy EventMatch endpoint."""

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @staticmethod
    def GET(event_uuid=None):
        """Get the event ID and return it."""
        if event_uuid:
            query = {'uuid': event_uuid}
        else:
            query = {'username': get_remote_user()}
        objs = [x for x in orm.EventMatch.select(**query).dicts()]
        if not len(objs):
            raise cherrypy.HttpError(404, 'Not Found')
        return objs[0]


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @staticmethod
    def POST(event_match_obj):
        """Create an Event Match obj in the database."""
        event_obj = orm.EventMatch(**event_match_obj).save()
        return EventMatch.GET(event_obj.uuid)

    @cherrypy.expose
    @staticmethod
    def DELETE(event_uuid):
        """Delete the event by uuid."""
        objs = orm.EventMatch().select(uuid=event_uuid)
        if len(objs):
            objs[0].delete_instance()


class Root(object):
    """CherryPy Root Object."""
    eventmatch = EventMatch()
