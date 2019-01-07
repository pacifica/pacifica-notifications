#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the database connection logic."""
import os
import mock
import peewee
from pacifica.notifications.orm import EventMatch, OrmSync, NotificationSystem


@mock.patch.object(EventMatch, 'database_connect')
def test_bad_db_connection(mock_db_connect):
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
    assert hit_exception


def test_no_table_goc_version():
    """Test the get or create version with no table."""
    OrmSync.dbconn_blocking()
    OrmSync.update_tables()
    NotificationSystem.drop_table()
    major, minor = NotificationSystem.get_or_create_version()
    assert major == 0
    assert minor == 0


def test_update_tables_twice():
    """Test updating tables twice to verify completeness."""
    OrmSync.dbconn_blocking()
    OrmSync.update_tables()
    OrmSync.update_tables()
