#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test script to run the command interface for testing."""
from __future__ import print_function
import sys
import os
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
try:
    import sh
except ImportError:
    import pbs

    class Sh:
        """Sh style wrapper."""

        def __getattr__(self, attr):
            """Return command object like sh."""
            return pbs.Command(attr)

        # pylint: disable=invalid-name
        @staticmethod
        def Command(attr):
            """Return command object like sh."""
            return pbs.Command(attr)
    sh = Sh()
import peewee
from pacifica.notifications.orm import EventMatch, NotificationSystem, EventLogMatch, EventLog
from pacifica.notifications.__main__ import cmd, main


class TestAdminCmdBase:
    """Test base class to setup update conditions."""

    virtualenv_dir = mkdtemp()

    @classmethod
    def _setup_venv(cls):
        """Setup the Python VirtualEnv."""
        sh.Command(sys.executable)('-m', 'virtualenv', '--python', sys.executable, cls.virtualenv_dir)

    @classmethod
    def _get_python_cmd(cls):
        """Get the Python Command object."""
        python_exe = os.path.basename(sys.executable)
        python_venv_cmd = None
        for exe_dir in ['bin', 'Scripts']:
            fpath = os.path.join(cls.virtualenv_dir, exe_dir, python_exe)
            if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
                python_venv_cmd = sh.Command(fpath)
        return python_venv_cmd

    # pylint: disable=invalid-name
    @classmethod
    def setUpClass(cls):
        """Setup a virtualenv and install the original version."""
        cls._setup_venv()
        cls._get_python_cmd()('-m', 'pip', 'install', 'pacifica-notifications==0.2.3', 'psycopg2')

    @classmethod
    def setUp(cls):
        """Setup the db for the test."""
        EventLogMatch.drop_table(safe=True)
        EventMatch.drop_table(safe=True)
        EventLog.drop_table(safe=True)
        NotificationSystem.drop_table(safe=True)
        cls._get_python_cmd()(
            '-c', 'import sys; from pacifica.notifications.orm import database_setup; sys.exit(database_setup())'
        )

    @classmethod
    def tearDownClass(cls):
        """Remove the virtualenv dir."""
        rmtree(cls.virtualenv_dir)


class TestAdminCmdSync(TestAdminCmdBase, TestCase):
    """Test the database upgrade scripting."""

    def test_dbchk(self):
        """Test that dbchk doesn't work."""
        self.assertEqual(cmd('dbchk'), -1)

    def test_dbchk_equal(self):
        """Test that dbchk doesn't work."""
        self.assertEqual(cmd('dbchk', '--equal'), -1)

    def test_main_error(self):
        """Test that dbchk doesn't work."""
        with self.assertRaises(peewee.OperationalError):
            main('--stop-after-a-moment')

    def test_dbsync(self):
        """Run the update by calling dbsync."""
        self.assertEqual(cmd('dbsync'), 0)

    def test_main(self):
        """Test that dbchk doesn't work."""
        cmd('dbsync')
        cmd('dbsync')
        hit_exception = False
        try:
            main('--stop-after-a-moment', '--cpconfig', os.path.join(os.path.dirname(__file__), '..', 'server.conf'))
        # pylint: disable=broad-except
        except Exception:
            hit_exception = True
        self.assertFalse(hit_exception)


class TestAdminCmdEvents(TestAdminCmdBase, TestCase):
    """Test the database upgrade scripting."""

    event_match_objs = [
        {
            'uuid': '7e487ebb-309f-4dd7-bb17-0287b4209e2e',
            'name': 'Event Match 01',
            'jsonpath': '$["data"]',
            'user': 'johndoe',
            'target_url': 'http://localhost/events'
        },
        {
            'uuid': '45736222-a4d5-48dd-99e2-ea54ae7f6bb7',
            'name': 'Event Match 02',
            'jsonpath': '$["data"]',
            'user': 'janedoe',
            'target_url': 'http://localhost/events'
        }
    ]
    event_log_objs = [
        {
            'uuid': '9419b5b6-6f11-439a-9585-42e272c97da4',
            'jsondata': '{}'
        },
        {
            'uuid': '474549ce-672c-4771-8b39-c4ecdd951691',
            'jsondata': '{}'
        },
        {
            'uuid': '390d52b7-0c50-415c-b750-2071520f05ed',
            'jsondata': '{}'
        }
    ]
    event_log_match_objs = [
        {
            'uuid': '40cab09f-547a-432f-8424-bd75a6993170',
            'event_log': '390d52b7-0c50-415c-b750-2071520f05ed',
            'event_match': '7e487ebb-309f-4dd7-bb17-0287b4209e2e',
            'policy_status_code': '201',
            'policy_resp_body': '{"something": "policy returned"}'
        },
        {
            'uuid': '4728abdb-58e7-4ee2-81a8-ce4ae69eeda4',
            'event_log': '474549ce-672c-4771-8b39-c4ecdd951691',
            'event_match': '45736222-a4d5-48dd-99e2-ea54ae7f6bb7',
            'policy_status_code': '201',
            'policy_resp_body': '{"something": "policy returned"}'
        },
        {
            'uuid': '0ebfebdd-7de7-47fd-bace-5294f13ef5c0',
            'event_log': '9419b5b6-6f11-439a-9585-42e272c97da4',
            'event_match': '45736222-a4d5-48dd-99e2-ea54ae7f6bb7',
            'policy_status_code': '201',
            'policy_resp_body': '{"something": "policy returned"}'

        }
    ]

    @classmethod
    def setUp(cls):
        """Call super method and create some data in the db."""
        super().setUp()
        cmd('dbsync')
        for event_match_hash in cls.event_match_objs:
            event_match_obj = EventMatch(**event_match_hash)
            event_match_obj.save(force_insert=True)
        for event_log_hash in cls.event_log_objs:
            event_log_obj = EventLog(**event_log_hash)
            event_log_obj.save(force_insert=True)
        for event_log_match_hash in cls.event_log_match_objs:
            event_log_match_obj = EventLogMatch(**event_log_match_hash)
            event_log_match_obj.save(force_insert=True)

    def test_eventget(self):
        """Test that dbchk doesn't work."""
        self.assertEqual(cmd('eventget'), 0)

    def test_eventget_with_args(self):
        """Test some of the arguments with eventget."""
        self.assertEqual(cmd('eventget', '--start-date', '2020-01-01 00:00:00', '--end-date', '2020-02-01 00:00:00'), 0)

    def test_eventget_wrong_order(self):
        """Test the reverse of start and end time."""
        with self.assertRaises(ValueError):
            cmd('eventget', '--start-date', '2020-03-01 00:00:00', '--end-date', '2020-02-01 00:00:00')

    def test_eventget_with_uuids(self):
        """Test some of the uuid arguments with eventget."""
        self.assertEqual(cmd('eventget', '9419b5b6-6f11-439a-9585-42e272c97da4'), 0)

    def test_eventpurge_with_uuids(self):
        """Test some of the uuid arguments with eventpurge."""
        self.assertEqual(cmd('eventpurge', '9419b5b6-6f11-439a-9585-42e272c97da4'), 0)

    def test_eventpurge_with_args(self):
        """Test some of the uuid arguments with eventpurge."""
        self.assertEqual(cmd('eventpurge', '--older-than-date', '2199-01-01 00:00:00'), 0)

    def test_eventpurge(self):
        """Test some eventpurge."""
        self.assertEqual(cmd('eventpurge'), 0)
