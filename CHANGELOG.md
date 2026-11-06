<!--
Copyright: (c) 2026, Richard Lynch
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Changelog

All notable changes to this collection are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the collection
uses [Semantic Versioning](https://semver.org/).

## [1.2.0] — 2026-11-06

### Changed

- `proxmox_ci_access` no longer prints a newly created API token's secret. The `pveum` call that creates the token is `no_log` (its output is the secret), and the secret is written once, mode 0600, to a new option `proxmox_ci_access_secret_dest` on the controller; the role prints only that path. A run that would create the token stops first when `proxmox_ci_access_secret_dest` is unset. Re-runs against an existing token are unchanged. Migrating: set `proxmox_ci_access_secret_dest` where a play may create the token.

## [1.1.0] — 2026-11-05

### Added

- Role `proxmox_lxc_mount_gate`: gates a container's start on a host mount with a pre-start hookscript that starts the units the mount depends on and refuses the start until the path is a real mountpoint, so `onboot: 1` is safe for a container whose bind mount comes from a filesystem that mounts late. Report-only by default; with apply it enables the units, wires the hookscript into the container config and sets `onboot: 1`. The guest, the path and the units are required options with no default.

### Changed

- CI, disclosure and release workflows call ansible-devkit v0.4.1.

## [1.0.0] — 2026-11-03

### Added

- Roles `deployment_proxmox_lxc` and `deployment_proxmox_vm` (guests from a template, with config-drift reporting), `proxmox_cloud_vm` (a VM from a cloud image with cloud-init), `proxmox_template_lxc` and `proxmox_iso_download`.
- Roles `proxmox_guest_firewall` (cluster and per-guest firewall files rendered and diffed before apply), `proxmox_storage_layout`, `proxmox_vzdump` (backup jobs), `proxmox_ci_access` and `proxmox_ci_ssh_access` (a scoped API token and SSH key for CI).
- Roles `proxmox_gpu_passthrough`, `intel_gpu_vaapi`, `intel_media_driver_build` and `proxmox_lxc_docker_fix` (on PVE 8), plus `vm_homeassistant` and `vm_truenas` guest builds.
- Every estate-specific value is a required option with no default.
