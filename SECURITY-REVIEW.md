# Pre-install security review — 2026-11-02

## Scope and result

Reviewed original fork revision `f9308e4da6c09b3f5b614447741b18b8c6bb05d2`.
An independent agent reviewed the original packaging and the hardening diff.
No HA installation, playback switch, or existing repository replacement was
performed during this work.

The hardened amd64 image builds, its linked libraries resolve, and its launcher
passes offline input-handling and identity-persistence checks. This is a
review candidate, not deployment approval: native aarch64 and live HAOS
PulseAudio/AppArmor/network tests are required before switching the speakers.

## Corrections

- Player source pinned to `cc7ee7c0d00bd2aa691a574a7d429d5cd13c858b`
  (Squeezelite 2.0.0-1612). Contains:
  - Ogg bounds/alignment fix:
    https://github.com/ralph-irving/squeezelite/commit/4e0ec3188320da7de059c571499e626ff8b3712f
  - Malformed-MP4 hang fix:
    https://github.com/ralph-irving/squeezelite/commit/afa8e834b2e2774016ca244a5f19f67ed0bd7d3b
- Debian base updated to 9.5.1 with immutable amd64 and arm64 image digests.
  Build-time apt upgrades apply available Debian security updates.
- Removed unused FFmpeg/libmad/player backends and inherited tempio executable.
  The initial scan found 24 fixable high package findings in tempio's bundled
  Go dependencies; the final scan no longer detects that executable.
- Restored default AppArmor. Removed privileged capabilities, HA config mount,
  full device access, Supervisor API permission, udev and host networking.
- Launcher uses local JSON options directly, quotes all arguments, writes names
  as literal text, validates server/identity, and execs the player.
- Manual startup, PulseAudio only, amd64/aarch64 support. See migration notes
  in squeezelite/DOCS.md.

## Local validation

- Rootless Podman amd64 build completed.
- Player reports 2.0.0-1612; ldd reports no missing libraries.
- All ten clone manifests/pins/scripts checked for consistency.
- Shell syntax, workflow YAML and git whitespace checks passed.
- Offline launcher runs with no network, read-only root filesystem, no
  capabilities and no-new-privileges. Tests cover literal percent/shell
  metacharacters, invalid server/MAC rejection, and generated MAC persistence.
- Tests substitute an argument-capture binary; they do not prove actual audio.
- CI builds and scans both supported architectures on native GitHub runners.

## Vulnerability scan

Trivy 0.76.1, official scanner image digest:
`sha256:2e6c00d711ab4ae41d8a30c2c1fd3bd3b62704c177bb120f95012e939edfb3df`.

Final local image ID:
`9cbdc62bd2c57914a033811d2441a11da1a556125f5ca4c89b49ae56a1d9ecdb`.

Scan generated at 2026-11-02T16:54:41Z with the current downloaded database.
No vulnerability suppression or ignore-unfixed option was used.

| Severity | Package findings |
|---|---:|
| Critical | 0 |
| High | 52 |
| Medium | 114 |
| Low | 147 |
| Unknown | 8 |

All 52 high findings lack a fixed version in this scan. They represent 13 unique
CVE IDs, repeated across binary packages; they are not 52 distinct exploits.
They remain findings, not accepted risks or automatically dismissed false
positives. Debian may assess affected functionality and severity differently
from the scanner. Review the vendor trackers before deployment:

| CVE | Flagged binary packages |
|---|---|
| CVE-2025-69720 | libtinfo6, ncurses-base, ncurses-bin |
| CVE-2026-119373 | libsqlite3-0 |
| CVE-2026-12064 | curl, libcurl4t64 |
| CVE-2026-16742 | libsystemd0, libudev1 |
| CVE-2026-37555 | libsndfile1 |
| CVE-2026-54369 | libacl1 |
| CVE-2026-76642 | util-linux family, bsdutils, login, mount |
| CVE-2026-78408 | util-linux family, bsdutils, login, mount |
| CVE-2026-78409 | util-linux family, bsdutils, login, mount |
| CVE-2026-78410 | util-linux family, bsdutils, login, mount |
| CVE-2026-8458 | curl, libcurl4t64 |
| CVE-2026-88806 | libx11-6, libx11-data, libx11-xcb1 |
| CVE-2026-9538 | perl-base |

Vendor tracker format:
`https://security-tracker.debian.org/tracker/CVE-ID`.

The CI gate fails on every critical finding and any high finding with an
available fix; it also retains the complete unfiltered report and prints the
unfixed high count. Passing CI is not a vulnerability-free certificate or
approval to deploy.

## Remaining limits

The host has no ARM emulation registered. aarch64 validation must run in the
native ARM CI job. HAOS default AppArmor, the PulseAudio socket/output selector,
and container-network access to MA require a separate staged trial.

Upstream optional TLS support does not configure certificate verification;
do not treat it as authenticated HTTPS. The intended local MA stream uses the
configured internal stream address. This update is not a claim to fix all
upstream parser bugs or Music Assistant queue/recommendation behavior.
