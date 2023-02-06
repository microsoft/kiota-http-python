# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2023-02-06

### Added

- Added the HTTP response status code on APIError class.
### Changed

- Fixed bug with middleware not respecting request options.

## [0.3.0] - 2023-01-20

### Changed

- Enabled configuring of middleware during client creation by passing custom options in call to create with default middleware. [#56](https://github.com/microsoft/kiota-http-python/issues/56)

## [0.2.4] - 2023-01-17

### Changed

- Changes the ResponeHandler parameter in RequestAdapter to be a RequestOption