<!--
Copyright: (c) 2026, Richard Lynch
SPDX-License-Identifier: GPL-3.0-or-later
-->

# richard_lynch.proxmox

Roles for running Proxmox VE nodes: LXC and VM guests from templates or cloud images, LXC templates, guest firewall rendering, storage layout, vzdump jobs, CI API and SSH access, kernel install, GPU passthrough and Intel VA-API media drivers, Docker-in-LXC fixes, and gating a container's start on a host mount.

## Roles

| Role | Description |
| ---- | ----------- |
| `deployment_proxmox_lxc` | Deploys an LXC container onto a Proxmox host |
| `deployment_proxmox_vm` | Deploys a VM onto a Proxmox host |
| `intel_gpu_vaapi` | Install Intel VA-API userspace and prove the GPU can actually be opened |
| `intel_media_driver_build` | Build a patched Intel iHD VA-API driver and install it alongside the bundled one |
| `proxmox_ci_access` | Create a least-privilege PVE user, role and API token for CI |
| `proxmox_ci_ssh_access` | Narrow CI SSH user + restricted sudoers on a PVE node |
| `proxmox_cloud_vm` | Create or converge one cloud-init Proxmox VM from a checksummed image |
| `proxmox_gpu_passthrough` | Free a GPU from vfio-pci on a Proxmox host so the host driver can bind it |
| `proxmox_guest_firewall` | Report, preview or apply the Proxmox firewall for a set of guests |
| `proxmox_iso_download` | Download an ISO or disk image from a URL into a Proxmox VE node's local ISO directory, re- downloading when the local copy is older than a set number of days, and set its path and storage volume as facts. |
| `proxmox_kernel_install` | Install an additional Proxmox kernel series alongside the running one |
| `proxmox_lxc_docker_fix` | Let Docker run in an unprivileged LXC on PVE 8.x (AppArmor workaround) |
| `proxmox_lxc_mount_gate` | Gate a Proxmox LXC's start on a host mount with a pre-start hookscript |
| `proxmox_storage_layout` | Dedicated PVE backup Directory storage on a thin LV (off the root LV) |
| `proxmox_template_lxc` | Create a template LXC in Proxmox |
| `proxmox_vzdump` | Reconcile a cluster-wide nightly vzdump backup job via pvesh |
| `vm_homeassistant` | Sets up a home assistant VM |
| `vm_truenas` | Creates a TrueNAS VM on Proxmox and pauses for the manual install |

## Install

```sh
ansible-galaxy collection install richard_lynch.proxmox
```

or pin it in `requirements.yml`:

```yaml
collections:
  - name: richard_lynch.proxmox
    version: "1.1.0"
```

Requires ansible-core >=2.19.0.

## Development

```sh
# from a checkout at ansible_collections/richard_lynch/proxmox
ansible-test sanity --docker
ansible-test units --docker
ansible-galaxy collection build
devkit conform                  # the repository standard (ansible-devkit)
devkit check all                # the static checks, configured by devkit.toml
```

CI, the disclosure gate and releases are the shared workflows of
[ansible-devkit](https://github.com/Richard-Lynch/ansible-devkit), called from
`.github/workflows/` at tag `v0.4.1`. A release is a merged pull
request that bumps `version` in `galaxy.yml` and adds the matching
`CHANGELOG.md` section. `export.manifest` lists every tracked path; update it in
the same commit as any file added or removed.

## Licence

GPL-3.0-or-later. See [LICENSE](LICENSE).
