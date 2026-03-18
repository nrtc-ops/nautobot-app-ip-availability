# v0.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Major features or milestones
- Changes to compatibility with Nautobot and/or other apps, libraries etc.

<!-- towncrier release notes start -->

## [v0.1.0a3 (2026-03-18)](https://github.com/nrtc-ops/nautobot-app-ip-availability/releases/tag/v0.1.0a3)

### Added

- [#pr4](https://github.com/nrtc-ops/nautobot-app-ip-availability/issues/pr4) - - Removed fields in find form
- [#pr4](https://github.com/nrtc-ops/nautobot-app-ip-availability/issues/pr4) - - Added "Member" role to reserved prefix creation
- [#pr4](https://github.com/nrtc-ops/nautobot-app-ip-availability/issues/pr4) - - Added expiration reservation job, deletes prefixes that are in (reserved status and role member) >= 2 months from now
