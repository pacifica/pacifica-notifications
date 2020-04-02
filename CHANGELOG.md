# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2020-04-02
### Added
- Pull #41 Add Python 3.7 and 3.8 by [@dmlb2000](https://github.com/dmlb2000)
- Pull #40 Add Admin Event Retry by [@dmlb2000](https://github.com/dmlb2000)
- Pull #39 Add Admin Event Get/Purge by [@dmlb2000](https://github.com/dmlb2000)
- Fix #33 Add Event Logging by [@dmlb2000](https://github.com/dmlb2000)

### Changed
- Pull #36 Update Testing and PyLint 2.0+ by [@dmlb2000](https://github.com/dmlb2000)
- Pull #35 Update Packaging URL by [@dmlb2000](https://github.com/dmlb2000)
- Pull #31 Add Ansible Travis by [@dmlb2000](https://github.com/dmlb2000)

## [0.4.1] - 2019-05-18
### Added
- Event subscription management API
- Event endpoint for notifying subscribers
- Model upgrade process
- ReadtheDocs supported Sphinx docs
- REST API for subscribing to events
  - PUT - Update a Subscription
  - POST - Create a Subscription
  - GET - Get a Subscription
  - DELETE - Delete a Subscription
- REST API for receiving events
  - POST - receive new event

### Changed
