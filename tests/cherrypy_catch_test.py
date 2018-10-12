#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is an example CherryPy based event catch used in testing."""
import cherrypy


# pylint: disable=too-few-public-methods
class Root(object):
    """Example root cherrypy class, method dispatcher required."""

    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    # pylint: disable=invalid-name
    # pylint: disable=no-self-use
    def POST(self):
        """Accept the post data and return it."""
        return cherrypy.request.json


if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/', {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    })
