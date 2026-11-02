# Squeezelite for Home Assistant audio

This fork runs upstream Squeezelite as a SlimProto client for Music Assistant or
Lyrion Music Server. Audio goes through Home Assistant's PulseAudio service to
the output selected in the add-on's Audio panel.

## Installation and configuration

Add `https://github.com/vectorcrumb/ha-addon-squeezelite` to the Home Assistant
add-on repositories. Install Squeezelite, but leave it stopped until configured.

In Music Assistant, enable the native Squeezelite player provider. Do not add
HA's SlimProto integration or another server competing for port 3483.

Set the add-on options, for example:

```yaml
name: Edifier M60
server: 192.168.30.10
log_level: info
clientmac: "02:00:00:00:60:01"
```

Use your MA server's address, optionally followed by its SlimProto port. The
server setting is required: broadcast discovery is deliberately not used.
If omitted, clientmac is generated once and persisted in the add-on's private
data. Give each simultaneously running clone a different clientmac.

In the add-on's Audio panel, select the attached USB speaker/DAC. Stop the old
audio player before testing this one. Leave Protection mode enabled. Start at
low volume. Automatic startup is disabled until you choose to enable it.

The client initiates the SlimProto and audio-stream connections through the
normal container network. MA's published stream address and port must therefore
be reachable from that network (typically the HA LAN address and port 8097).
No host ports are published by this add-on.

## Security and compatibility changes in 0.0.22

- Pinned Squeezelite source includes the October 2026 Ogg bounds-check and
  malformed-MP4 fixes.
- Debian base 9.5.1 is pinned by architecture-specific digest; build-time apt
  upgrades still apply Debian security updates.
- Default AppArmor and Protection mode stay enabled. No privileged capabilities,
  full device access, host networking, writable HA configuration mount or
  Supervisor API access are requested.
- Only the PulseAudio binary and its codec dependencies are included. FFmpeg,
  libmad, direct ALSA/PortAudio output, visualizer shared memory, GPIO and IR
  support are not included.
- Free-form options, output, build and nice settings are removed. Existing
  installations must remove those old options before updating.
- Supported architectures are aarch64 and amd64, matching the maintained base.
  Legacy 32-bit architecture listings are removed.
- The Squeezelite process still runs as container root under the HA base's init
  system. Confinement is provided by the container and AppArmor; this is not a
  claim that the process is unprivileged inside the container.

Music Assistant continues to own the queue. This change does not itself fix
radio selection, listening-history or provider recommendation bugs.

## Validation before deployment

Build an image for the target architecture, run `tests/runtime.py` against the
amd64 image, and scan the final image with a current vulnerability database.
Review all critical/high findings, including unfixed ones. A clean package scan
does not cover every manually compiled C parser or prove playback reliability.
Test HA audio routing, AppArmor compatibility, track transitions and restart
recovery before removing the previous player.

See [the review record](../SECURITY-REVIEW.md) for the validation actually run.
