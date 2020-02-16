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
from pacifica.notifications.orm import EventMatch, NotificationSystem
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
        EventMatch.drop_table(safe=True)
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
