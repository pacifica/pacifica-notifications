#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The WSGI interface module for notifications."""
import cherrypy
from pacifica.notifications.rest import Root, error_page_default
from pacifica.notifications.globals import CHERRYPY_CONFIG

cherrypy.config.update({'error_page.default': error_page_default})
# pylint doesn't realize that application is actually a callable
# pylint: disable=invalid-name
application = cherrypy.Application(Root(), '/', CHERRYPY_CONFIG)
# pylint: enable=invalid-name
