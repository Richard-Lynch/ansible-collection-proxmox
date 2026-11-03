# proxmox_iso_download

Downloads an ISO or disk image from a URL into a Proxmox VE node's local ISO
directory, and sets facts naming where it landed. The collection's VM
roles include it to fetch their install media.

## What it does

1. Derives the destination from the URL's basename:
   `/var/lib/vz/template/iso/<basename>`.
2. If that file exists, computes how many days ago it last changed (its
   `ctime`).
3. Downloads the URL to that path (`ansible.builtin.get_url`, `force: true`,
   mode `0644`) when the file is absent, or when it is at least
   `proxmox_iso_days_limit` days old.

No checksum is verified.

## Inputs

There is no argument spec; the role reads these variables.

| Variable                 | Required         | Default                             | Description                                                    |
| ------------------------ | ---------------- | ----------------------------------- | -------------------------------------------------------------- |
| `proxmox_iso_url`        | yes, in practice | an Ubuntu 24.04 live-server ISO URL | URL of the file to download                                    |
| `proxmox_iso_days_limit` | no               | `100`                               | Re-download when the local copy is at least this many days old |

## Facts set

| Fact                        | Value                                                                        |
| --------------------------- | ---------------------------------------------------------------------------- |
| `proxmox_iso_download_path` | `/var/lib/vz/template/iso/<basename>`                                        |
| `proxmox_iso`               | `local:iso/<basename>`, the PVE volume id of the file on the `local` storage |

## Usage

Run on the Proxmox VE node that should hold the file:

```yaml
- hosts: pve_nodes
  become: true
  tasks:
    - name: Fetch install media
      ansible.builtin.include_role:
        name: richard_lynch.proxmox.proxmox_iso_download
      vars:
        proxmox_iso_url: https://example.com/images/installer.iso
```
