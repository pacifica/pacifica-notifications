#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The main module for executing the CherryPy server."""
import os
from sys import argv as sys_argv
from datetime import datetime, timedelta
from time import sleep
from argparse import ArgumentParser, SUPPRESS
from threading import Thread
import cherrypy
from peewee import OperationalError
from .tasks import dispatch_orm_event
from .orm import OrmSync, EventLog, NotificationSystem, eventget, eventpurge, SCHEMA_MAJOR, SCHEMA_MINOR
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


def bool2cmdint(command_bool):
    """Convert a boolean to either 0 for true  or -1 for false."""
    if command_bool:
        return 0
    return -1


def _eventget(args):
    """Parse the dates and validate types before calling real eventget."""
    if not args.start:
        args.start = (datetime.now() - timedelta(days=1))
    else:
        args.start = datetime.strptime(args.start, args.format)
    if not args.end:
        args.end = datetime.now()
    else:
        args.end = datetime.strptime(args.end, args.format)
    if args.start > args.end:
        raise ValueError('Start time {} should be less than end time {}'.format(args.start, args.end))
    return bool2cmdint(eventget(args))


def _eventpurge(args):
    """Parse the dates and validate types before calling real eventpurge."""
    if not args.older_than:
        args.older_than = (datetime.now() - timedelta(days=1))
    else:
        args.older_than = datetime.strptime(args.older_than, args.format)
    return bool2cmdint(eventpurge(args))


def _eventretry(args):
    """Retry events given on the cmdline."""
    EventLog.database_connect()
    event_objs = list(EventLog.select().where(EventLog.uuid << args.events).execute())
    EventLog.database_close()
    results = []
    for event_obj in event_objs:
        results.extend(dispatch_orm_event(event_obj))
    sleep(3)
    for result in results:
        print('{} - {}'.format(result.task_id, result.wait(disable_sync_subtasks=False)))
    return 0


def _add_dbsync_parser(subparsers):
    """Add the dbsync subcommand arguments."""
    db_parser = subparsers.add_parser(
        'dbsync',
        description='Update or Create the Database.'
    )
    db_parser.set_defaults(func=dbsync)


def _add_dbchk_parser(subparsers):
    """Add the dbchk subcommand arguments."""
    dbchk_parser = subparsers.add_parser(
        'dbchk',
        description='Check database against current version.'
    )
    dbchk_parser.add_argument(
        '--equal', default=False,
        dest='check_equal', action='store_true'
    )
    dbchk_parser.set_defaults(func=dbchk)


def _add_eventget_parser(subparsers):
    """Add the eventget subcommand arguments."""
    dbchk_parser = subparsers.add_parser(
        'eventget',
        description='Get events from the log.'
    )
    dbchk_parser.add_argument(
        'events', nargs='*', type=str, help='Events to get'
    )
    dbchk_parser.add_argument(
        '--limit', default=10,
        dest='limit', type=int, help='Number of events to get'
    )
    dbchk_parser.add_argument(
        '--date-format', default='%Y-%m-%d %H:%M:%S',
        dest='format', type=str, help='Date format for start/end times'
    )
    dbchk_parser.add_argument(
        '--start-date', default=None,
        dest='start', type=str, help='Start date and time'
    )
    dbchk_parser.add_argument(
        '--end-date', default=None,
        dest='end', type=str, help='End date and time'
    )
    dbchk_parser.set_defaults(func=_eventget)


def _add_eventpurge_parser(subparsers):
    """Add the eventpurge subcommand arguments."""
    dbchk_parser = subparsers.add_parser(
        'eventpurge',
        description='Purge events from the log.'
    )
    dbchk_parser.add_argument(
        'events', nargs='*', type=str, help='Events to purge'
    )
    dbchk_parser.add_argument(
        '--date-format', default='%Y-%m-%d %H:%M:%S',
        dest='format', type=str, help='Date format for start/end times'
    )
    dbchk_parser.add_argument(
        '--older-than-date', default=None,
        dest='older_than', type=str, help='Events older than given date'
    )
    dbchk_parser.set_defaults(func=_eventpurge)


def _add_eventretry_parser(subparsers):
    """Add the eventretry subcommand arguments."""
    dbchk_parser = subparsers.add_parser(
        'eventretry',
        description='Retry events from the log.'
    )
    dbchk_parser.add_argument(
        'events', nargs='*', type=str, help='Events to purge'
    )
    dbchk_parser.set_defaults(func=_eventretry)


def cmd(*argv):
    """Admin command line tool."""
    parser = ArgumentParser(description='Notifications admin tool.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str, default=CONFIG_FILE,
        dest='config', help='notifications config file'
    )
    parser.set_defaults(func=lambda _args: parser.print_help())
    subparsers = parser.add_subparsers(help='sub-command help')
    _add_dbsync_parser(subparsers)
    _add_dbchk_parser(subparsers)
    _add_eventget_parser(subparsers)
    _add_eventpurge_parser(subparsers)
    _add_eventretry_parser(subparsers)
    if not argv:  # pragma: no cover
        argv = sys_argv[1:]
    args = parser.parse_args(argv)
    return args.func(args)


def main(*argv):
    """Main method to start the httpd server."""
    parser = ArgumentParser(description='Run the notifications server.')
    parser.add_argument(
        '-c', '--config', metavar='CONFIG', type=str,
        default=CONFIG_FILE, dest='config',
        help='notifications config file'
    )
    parser.add_argument(
        '--cpconfig', metavar='CONFIG', type=str,
        default=CHERRYPY_CONFIG, dest='cpconfig',
        help='cherrypy config file'
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
    if not argv:  # pragma: no cover
        argv = sys_argv[1:]
    args = parser.parse_args(argv)
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
    cherrypy.quickstart(Root(), '/', args.cpconfig)


def dbsync(args):
    """Create/Update the database schema to current code."""
    os.environ['NOTIFICATIONS_CONFIG'] = args.config
    OrmSync.dbconn_blocking()
    return bool2cmdint(OrmSync.update_tables())


def dbchk(args):
    """Check to see if the database is safe to use."""
    os.environ['NOTIFICATIONS_CONFIG'] = args.config
    OrmSync.dbconn_blocking()
    if args.check_equal:
        return bool2cmdint(NotificationSystem.is_equal())
    return bool2cmdint(NotificationSystem.is_safe())
