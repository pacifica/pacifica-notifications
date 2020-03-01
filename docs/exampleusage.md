# Example Usage

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
  "auth": {},
  "target_url": "http://www.example.com/receive",
  "error": null
}
```

#### Create Event Subscription with Authentication

Request:
```
POST /eventmatch
Http-Remote-User: dmlb2001
Content-Type: application/json
{
  "name": "My Event Match",
  "jsonpath": "data",
  "auth": {
    "type": "basic",
    "basic": {
      "username": "myusername",
      "password": "password"
    }
  },
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
  "auth": {
    "type": "basic",
    "basic": {
      "username": "myusername",
      "password": "password"
    }
  },
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
  "auth": {},
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
  "auth": {},
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

## Command Line Usage

There are several command line options to manage the database schema
and the data within. There are two commands to verify the schema is
updated and to update the schema if necessary. There are also
commands to manage the growing events that are tracked there.

### Schema Management Commands

The database schema can be verified using the `dbchk` subcommand.

```
$ pacifica-notifications-cmd dbchk; echo $?
0 or -1
```

If the result is `-1` then the database is not updated and should be
updated. To perform this run the `dbsync` subcommand to update the
schema.

```
$ pacifica-notifications-cmd dbsync; echo $?
0
```

The database schema is now updated and the service can now run.

### Event Log Management

Events and what matches were calculated are logged in the database
and need to be purged on a regular basis depending on the volume of
events received. Events can also be queried to view what matches were
calculated at the time they were received.

```
$ pacifica-notifications-cmd eventget
Event - a83ead91-8bff-4819-a0a1-d7dcf430b817
{...Some event data...}
    ELM 1791be8f-d9cc-418c-b976-b2a747b58678 (2020-02-29T20:44:17.923416) policy 201 target 200
    ELM ca028c49-5d87-4ee9-8c2b-620e7c32a10c (2020-02-30T05:13:40.123416) policy 201 target 200
```

To purge events from the log the `eventpurge` subcommand is used.

```
$ pacifica-notifications-cmd eventpurge --older-than-date '2020-01-01 00:00:00' --limit 1000; echo $?
0
```
