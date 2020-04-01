#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Celery tasks module."""
from datetime import datetime
from json import dumps, loads
import requests
from requests.exceptions import RequestException
from celery import Celery
from .orm import EventMatch, EventLog, EventLogMatch
from .jsonpath import parse, find
from .config import get_config

CELERY_APP = Celery(
    'notifications',
    broker=get_config().get('celery', 'broker_url'),
    backend=get_config().get('celery', 'backend_url')
)


@CELERY_APP.task
def dispatch_event(event_obj):
    """Get all the events and see which match."""
    EventLog.database_connect()
    orm_event = EventLog.create(
        jsondata=dumps(event_obj)
    )
    orm_event.save()
    EventLog.database_close()
    dispatch_orm_event(orm_event)


def dispatch_orm_event(orm_event):
    """Dispatch the event from an existing orm obj."""
    results = []
    event_obj = loads(orm_event.jsondata)
    EventMatch.database_connect()
    eventmatch_objs = EventMatch.select().where(
        (EventMatch.deleted >> None) &
        (EventMatch.disabled >> None)
    )
    EventMatch.database_close()
    for eventmatch in eventmatch_objs:
        jsonpath_expr = parse(eventmatch.jsonpath)
        if find(jsonpath_expr, event_obj):
            results.append(query_policy.delay(eventmatch.to_hash(), event_obj, orm_event.uuid))
    return results


def disable_eventmatch(eventmatch_uuid, error):
    """Disable the eventmatch obj."""
    EventMatch.database_connect()
    with EventMatch.atomic():
        eventmatch = EventMatch.get(EventMatch.uuid == eventmatch_uuid)
        eventmatch.disabled = datetime.now()
        eventmatch.error = error
        eventmatch.save()
    EventMatch.database_close()


def create_log_match(eventmatch, event_log_uuid, policy_resp):
    """Create the EventLogMatch object."""
    EventLogMatch.database_connect()
    orm_elm = EventLogMatch.create(
        event_log=event_log_uuid,
        event_match=eventmatch['uuid'],
        policy_status_code=policy_resp.status_code,
        policy_resp_body=policy_resp.text
    )
    orm_elm.save()
    EventLogMatch.database_close()
    return orm_elm.uuid


def update_log_match(elm_uuid, target_resp):
    """Update the EventLogMatch object with the target resp."""
    EventLogMatch.database_connect()
    orm_elm = EventLogMatch.get_by_id(elm_uuid)
    orm_elm.target_status_code = target_resp.status_code
    orm_elm.target_resp_body = target_resp.text
    orm_elm.save()
    EventLogMatch.database_close()


@CELERY_APP.task
def query_policy(eventmatch, event_obj, event_log_uuid):
    """Query policy server to see if the event should be routed."""
    resp = requests.post(
        '{}/events/{}'.format(
            get_config().get('notifications', 'policy_url'),
            eventmatch['user']
        ),
        data=dumps(event_obj),
        headers={'Content-Type': 'application/json'}
    )
    resp_major = int(int(resp.status_code)/100)
    if resp_major == 5:
        create_log_match(eventmatch, event_log_uuid, resp)
        disable_eventmatch(eventmatch['uuid'], resp.text)
    if resp_major == 4:
        return
    if resp_major == 2:
        elm_uuid = create_log_match(eventmatch, event_log_uuid, resp)
        route_event.delay(eventmatch, event_obj, elm_uuid)


def event_auth_to_requests(eventmatch, headers):
    """Convert the eventmatch authentication to requests arguments."""
    requests_kwargs = {}
    if eventmatch.get('auth').get('type', None) == 'basic':
        auth_obj = eventmatch.get('auth').get('basic', {})
        requests_kwargs['auth'] = (auth_obj.get('username', ''), auth_obj.get('password', ''))
    elif eventmatch.get('auth').get('type', None) == 'header':
        auth_obj = eventmatch.get('auth').get('header', {})
        headers['Authorization'] = '{} {}'.format(
            auth_obj.get('type', ''),
            auth_obj.get('credentials', '')
        )
    return requests_kwargs


@CELERY_APP.task
def route_event(eventmatch, event_obj, elm_uuid):
    """Route the event to the target url."""
    try:
        new_extensions = event_obj.get('extensions', {})
        new_extensions.update(eventmatch.get('extensions', {}))
        event_obj['extensions'] = new_extensions
        headers = {'Content-Type': 'application/json'}
        extra_args = event_auth_to_requests(eventmatch, headers)
        resp = requests.post(
            eventmatch['target_url'],
            data=dumps(event_obj),
            headers=headers,
            **extra_args
        )
    except RequestException as ex:
        disable_eventmatch(eventmatch['uuid'], str(ex))
        return
    resp_major = int(int(resp.status_code)/100)
    if resp_major in (5, 4):
        disable_eventmatch(eventmatch['uuid'], resp.text)
    update_log_match(elm_uuid, resp)
