#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The main module for executing the CherryPy server."""
from time import sleep
from argparse import ArgumentParser, SUPPRESS
from threading import Thread
import cherrypy
from pacifica.notifications.orm import database_setup
from pacifica.notifications.rest import Root, error_page_default
from pacifica.notifications.globals import CHERRYPY_CONFIG


def stop_later(doit=False):
    """Used for unit testing stop after 60 seconds."""
    if not doit:  # pragma: no cover
        return

    def sleep_then_exit():
        """
        Sleep for 20 seconds then call cherrypy exit.

        Hopefully this is long enough for the end-to-end tests to finish
        """
        sleep(20)
        cherrypy.engine.exit()
    sleep_thread = Thread(target=sleep_then_exit)
    sleep_thread.daemon = True
    sleep_thread.start()


def main():
    """Main method to start the httpd server."""
    parser = ArgumentParser(description='Run the notifications server.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str, default=CHERRYPY_CONFIG,
        dest='config', help='cherrypy config file'
    )
    parser.add_argument(
        '-p', '--port', metavar='PORT', type=int, default=8070, dest='port',
        help='port to listen on'
    )
    parser.add_argument(
        '-a', '--address', metavar='ADDRESS', default='localhost',
        dest='address', help='address to listen on'
    )
    parser.add_argument(
        '--stop-after-a-moment', help=SUPPRESS, default=False,
        dest='stop_later', action='store_true'
    )
    args = parser.parse_args()
    database_setup()
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(Root(), '/', args.config)


if __name__ == '__main__':
    main()
