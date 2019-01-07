#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The main module for executing the CherryPy server."""
import os
from time import sleep
from argparse import ArgumentParser, SUPPRESS
from threading import Thread
import cherrypy
from peewee import OperationalError
from .orm import OrmSync, NotificationSystem, SCHEMA_MAJOR, SCHEMA_MINOR
from .rest import Root, error_page_default
from .globals import CHERRYPY_CONFIG, CONFIG_FILE


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


def cmd():
    """Admin command line tool."""
    parser = ArgumentParser(description='Notifications admin tool.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str, default=CONFIG_FILE,
        dest='config', help='notifications config file'
    )
    subparsers = parser.add_subparsers(help='sub-command help')
    db_parser = subparsers.add_parser(
        'dbsync',
        description='Update or Create the Database.'
    )
    db_parser.set_defaults(func=dbsync)
    dbchk_parser = subparsers.add_parser(
        'dbchk',
        description='Check database against current version.'
    )
    dbchk_parser.add_argument(
        '--equal', default=False,
        dest='check_equal', action='store_true'
    )
    dbchk_parser.set_defaults(func=dbchk)
    args = parser.parse_args()
    return args.func(args)


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
    OrmSync.dbconn_blocking()
    if not NotificationSystem.is_safe():
        raise OperationalError('Database version too old {} update to {}'.format(
            '{}.{}'.format(*(NotificationSystem.get_version())),
            '{}.{}'.format(SCHEMA_MAJOR, SCHEMA_MINOR)
        ))
    stop_later(args.stop_later)
    cherrypy.config.update({'error_page.default': error_page_default})
    cherrypy.config.update({
        'server.socket_host': args.address,
        'server.socket_port': args.port
    })
    cherrypy.quickstart(Root(), '/', args.config)


def bool2cmdint(command_bool):
    """Convert a boolean to either 0 for true  or -1 for false."""
    if command_bool:
        return 0
    return -1


def dbsync(args):
    """Create/Update the database schema to current code."""
    os.environ['NOTIFICATIONS_CONFIG'] = args.config
    OrmSync.dbconn_blocking()
    return OrmSync.update_tables()


def dbchk(args):
    """Check to see if the database is safe to use."""
    os.environ['NOTIFICATIONS_CONFIG'] = args.config
    OrmSync.dbconn_blocking()
    if args.check_equal:
        return bool2cmdint(NotificationSystem.is_equal())
    return bool2cmdint(NotificationSystem.is_safe())


if __name__ == '__main__':
    main()
