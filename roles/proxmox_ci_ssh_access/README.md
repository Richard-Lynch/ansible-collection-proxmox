# proxmox_ci_ssh_access

Creates a **narrow CI OS user** on a PVE node so a CI runner can run the few host commands a
staging job needs (`pct`/`qm`/`pvesh`) over SSH — **without root access**.

## What it creates (idempotent)
- User `proxmox_ci_ssh_user` (login shell, home dir)
- `authorized_keys` with **only** the runner's key (`exclusive: true`)
- a sudoers drop-in (`proxmox_ci_ssh_sudoers_file`, default `/etc/sudoers.d/proxmox-ci`) — NOPASSWD
  sudo for **only** `pct`, `qm`, `pvesh` (validated with `visudo`)

Deliberately excludes a real shell's worth of power — no package mgmt, no `pvecm`, no network
reconfig. A compromised runner can drive guests but can't reconfigure the node.

## Inputs
`proxmox_ci_ssh_user` and `proxmox_ci_ssh_pubkey` (required — the login name and the runner's
public key). See `meta/argument_specs.yml`.

## Usage
```yaml
- hosts: proxmox              # every PVE node a CI job may land on
  roles:
    - role: richard_lynch.proxmox.proxmox_ci_ssh_access
      vars:
        proxmox_ci_ssh_user: cistaging
        proxmox_ci_ssh_pubkey: "{{ lookup('ansible.builtin.file', 'files/ci_runner.pub') }}"
```

## Testing
`molecule/default/` runs in check mode: asserts the sudoers is restricted to pct/qm/pvesh only.
