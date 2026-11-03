<!--
Copyright: (c) 2026, Richard Lynch
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Changelog

All notable changes to this collection are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the collection
uses [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-11-03

### Added

- Roles `deployment_proxmox_lxc` and `deployment_proxmox_vm` (guests from a template, with config-drift reporting), `proxmox_cloud_vm` (a VM from a cloud image with cloud-init), `proxmox_template_lxc` and `proxmox_iso_download`.
- Roles `proxmox_guest_firewall` (cluster and per-guest firewall files rendered and diffed before apply), `proxmox_storage_layout`, `proxmox_vzdump` (backup jobs), `proxmox_ci_access` and `proxmox_ci_ssh_access` (a scoped API token and SSH key for CI).
- Roles `proxmox_gpu_passthrough`, `intel_gpu_vaapi`, `intel_media_driver_build` and `proxmox_lxc_docker_fix` (on PVE 8), plus `vm_homeassistant` and `vm_truenas` guest builds.
- Every estate-specific value is a required option with no default.
