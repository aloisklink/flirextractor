# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2020-11-24

### Fixed

- Improved Error thrown by `get_thermal_batch()` when a non-radiometric
  image is passed.

## [1.0.2] - 2020-07-09

### Fixed

- Add a `py.typed` file to show that we have typed Python annotations under
  PEP 561.

## [1.0.1] - 2020-05-27

### Fixed

- Add support for Pillow version ^7.0.0.

## [1.0.0] - 2019-11-15

Update version numbering to v1.0.0 as the API should remain stable.

## [0.1.1] - 2019-11-15

### Fixed

- Fix FLIR images stored in `.png` format from loading in big-endian format.
- Updated README.md
- Use atmospheric constants from FLIR metadata if they exist
