# Pacifica Notifications Service
[![Build Status](https://travis-ci.org/pacifica/pacifica-notifications.svg?branch=master)](https://travis-ci.org/pacifica/pacifica-notifications)
[![Build Status](https://ci.appveyor.com/api/projects/status/c7jvfsgokp1txdso?svg=true)](https://ci.appveyor.com/project/dmlb2000/pacifica-notifications)
[![Maintainability](https://api.codeclimate.com/v1/badges/58b2e71aab6bd1af0609/maintainability)](https://codeclimate.com/github/pacifica/pacifica-notifications/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/58b2e71aab6bd1af0609/test_coverage)](https://codeclimate.com/github/pacifica/pacifica-notifications/test_coverage)

Pacifica notification service to catch internal state of data and notify on that state

## Overview

This service is a (Pacifica Policy)[https://github.com/pacifica/pacifica-policy.git]
based routing mechanism for data subscribers to execute workflows based on the
availability of data in Pacifica.

The (Pacifica Metadata)[https://github.com/pacifica/pacifica-metadata.git] service
emits (CloudEvents)[https://github.com/cloudevents/spec] when new data is accepted.
This service is intended to recieve and route those events to users that are
allowed based on Pacifica Policy.

## API Reference

There are two REST APIs available on this service. The first api accepts cloud events
for processing. The second api allows users to subscribe to events and specify
routing target urls to send those events.

### Cloud Events Recieve

```
POST /receive
Content-Type: application/json
... JSON Cloud Event ...
```

### Subscriptions

The subscriptions API is a REST style API accessed on `/eventmatch`.

#### Create Event Subscription

Request:
```
POST /eventmatch
Http-Remote-User: dmlb2001
Content-Type: application/json
{
  "name": "My Event Match",
  "jsonpath": "data",
  "target_url": "http://www.example.com/recieve"
}
```

Response:
```
Content-Type: application/json
{
  "user": "dmlb2001",
  "updated": "2018-08-02T13:53:05.838827",
  "uuid": "466725b0-cbe1-45cd-b034-c3209aa4b6e0",
  "deleted": null,
  "version": "v0.1",
  "jsonpath": "data",
  "disabled": null,
  "created": "2018-08-02T13:53:05.838827",
  "name": "My Event Match",
  "extensions": {},
  "target_url": "http://www.example.com/receive",
  "error": null
}
```

#### Get Event Subscription

Request:
```
GET /eventmatch/466725b0-cbe1-45cd-b034-c3209aa4b6e0
Http-Remote-User: dmlb2001
Content-Type: application/json
```

Response:
```
Content-Type: application/json
{
  "user": "dmlb2001",
  "updated": "2018-08-02T13:53:05.838827",
  "uuid": "466725b0-cbe1-45cd-b034-c3209aa4b6e0",
  "deleted": null,
  "version": "v0.1",
  "jsonpath": "data",
  "disabled": null,
  "created": "2018-08-02T13:53:05.838827",
  "name": "My Event Match",
  "extensions": {},
  "target_url": "http://www.example.com/receive",
  "error": null
}
```

#### Update Event Subscription

Request:
```
PUT /eventmatch/466725b0-cbe1-45cd-b034-c3209aa4b6e0
Http-Remote-User: dmlb2001
Content-Type: application/json
{
  "target_url": "http://api.example.com/receive"
}
```

Response:
```
Content-Type: application/json
{
  "user": "dmlb2001",
  "updated": "2018-08-02T13:53:05.838827",
  "uuid": "466725b0-cbe1-45cd-b034-c3209aa4b6e0",
  "deleted": null,
  "version": "v0.1",
  "jsonpath": "data",
  "disabled": null,
  "created": "2018-08-02T13:53:05.838827",
  "name": "My Event Match",
  "extensions": {},
  "target_url": "http://api.example.com/receive",
  "error": null
}
```

#### Delete Event Subscription

Request:
```
DELETE /eventmatch/466725b0-cbe1-45cd-b034-c3209aa4b6e0
```

Response:
```
HTTP/1.1 200 OK
```
