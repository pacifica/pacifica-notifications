#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The Celery tasks module."""
from os import getenv
from datetime import datetime
from json import dumps
from jsonpath_rw import parse
import requests
from celery import Celery
from pacifica.notifications.orm import EventMatch

CELERY_APP = Celery(
    'notifications',
    broker=getenv('BROKER_URL', 'pyamqp://'),
    backend=getenv('BACKEND_URL', 'rpc://')
)


@CELERY_APP.task
def dispatch_event(event_obj):
    """Get all the events and see which match."""
    EventMatch.connect()
    eventmatch_objs = EventMatch.select().where(
        (EventMatch.deleted is None) &
        (EventMatch.disabled is None)
    )
    EventMatch.close()
    for eventmatch in eventmatch_objs:
        jsonpath_expr = parse(eventmatch.jsonpath)
        if jsonpath_expr.find(event_obj):
            query_policy.delay(eventmatch, event_obj)


def disable_eventmatch(eventmatch, error):
    """Disable the eventmatch obj."""
    eventmatch.disabled = datetime.now()
    eventmatch.error = error
    EventMatch.connect()
    with EventMatch.atomic():
        eventmatch.save()
    EventMatch.close()


@CELERY_APP.task
def query_policy(eventmatch, event_obj):
    """Query policy server to see if the event should be routed."""
    resp = requests.post(
        '{}/events'.format(getenv('POLICY_URL', 'http://127.0.0.1:8181')),
        data=dumps(event_obj),
        headers={'Content-Type', 'application/cloudevents+json'}
    )
    resp_major = int(resp.status_code)/100
    if resp_major == 5:
        disable_eventmatch(eventmatch, resp.body.read())
    if resp_major == 4:
        return
    if resp_major == 2:
        route_event.delay(eventmatch, event_obj)


@CELERY_APP.task
def route_event(eventmatch, event_obj):
    """Route the event to the target url."""
    resp = requests.post(
        eventmatch.target_url,
        data=dumps(event_obj),
        headers={'Content-Type', 'application/cloudevents+json'}
    )
    resp_major = int(resp.status_code)/100
    if resp_major == 5 and resp_major == 4:
        disable_eventmatch(eventmatch, resp.body.read())