#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the database connection logic."""
import os
from unittest import TestCase
import mock
import peewee
from pacifica.notifications.orm import EventMatch, OrmSync, NotificationSystem
from .common_test import NotificationsCPTest


class TestDBConnections(NotificationsCPTest, TestCase):
    """Testing the database connection utilities."""

    @mock.patch.object(EventMatch, 'database_connect')
    def test_bad_db_connection(self, mock_db_connect):
        """Test a failed db connection."""
        mock_db_connect.side_effect = peewee.OperationalError(
            mock.Mock(), 'Error')
        hit_exception = False
        os.environ['DATABASE_CONNECT_ATTEMPTS'] = '1'
        os.environ['DATABASE_CONNECT_WAIT'] = '1'
        try:
            OrmSync.dbconn_blocking()
        except peewee.OperationalError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_no_table_goc_version(self):
        """Test the get or create version with no table."""
        OrmSync.dbconn_blocking()
        OrmSync.update_tables()
        NotificationSystem.drop_table()
        major, minor = NotificationSystem.get_or_create_version()
        self.assertEqual(major, 0)
        self.assertEqual(minor, 0)
