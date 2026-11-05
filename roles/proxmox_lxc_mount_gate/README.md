# proxmox_lxc_mount_gate

Gates a Proxmox VE container's start on a host mount, so `onboot: 1` is safe for
a container whose bind mount comes from a filesystem that mounts late.

## The problem it solves

A container's bind mount (`mpN: /mnt/x,mp=/data`) takes whatever is at the host
path when the container starts. If that path is a filesystem that comes up after
the node has booted (an iSCSI LUN, a network block device, a disk served by
another guest on the same node), a container that autostarts first binds the
**empty** directory underneath, and everything inside it runs against nothing,
with no error anywhere. The usual workaround is `onboot: 0` and a manual start
after every reboot.

## What it does

Writes a Proxmox VE **pre-start hookscript** into a snippets directory. Proxmox
VE runs it as `<hookscript> <vmid> pre-start` before the container starts, and a
non-zero exit refuses the start. The script:

1. starts each unit in `proxmox_lxc_mount_gate_requires_units`, in order, then
   the mount unit;
2. waits until `proxmox_lxc_mount_gate_mount_path` is a real mountpoint,
   starting the mount unit again on each try
   (`proxmox_lxc_mount_gate_wait_tries` × `proxmox_lxc_mount_gate_wait_delay`
   seconds, 30 × 5 by default);
3. exits 1, refusing the start, if the path never becomes a mountpoint.

Every other phase is a no-op.

**Generate, don't apply.** With `proxmox_lxc_mount_gate_apply: false` (the
default) the role writes the hookscript and reports what apply would change; how
the node boots is not changed. With `true` it also:

- enables and starts the required units and the mount unit, and fails if the
  path is not then a mountpoint;
- sets `hookscript: <storage>:snippets/<file>` in `/etc/pve/lxc/<ctid>.conf`;
- sets `onboot: 1` in the same file.

It never starts, stops or reboots the container. The only real test of the
ordering is a reboot of the node.

## Inputs

See [`meta/argument_specs.yml`](meta/argument_specs.yml).

| Option                                    | Required | Default                | Meaning                                                       |
| ----------------------------------------- | -------- | ---------------------- | ------------------------------------------------------------- |
| `proxmox_lxc_mount_gate_ctid`             | yes      |                        | The container whose start is gated.                           |
| `proxmox_lxc_mount_gate_mount_path`       | yes      |                        | Absolute host path that must be a mountpoint.                 |
| `proxmox_lxc_mount_gate_mount_unit`       | yes      |                        | Its systemd `.mount` unit.                                    |
| `proxmox_lxc_mount_gate_requires_units`   | no       | `[]`                   | Units started, in order, before the mount unit.               |
| `proxmox_lxc_mount_gate_wait_tries`       | no       | `30`                   | Checks before the start is refused.                           |
| `proxmox_lxc_mount_gate_wait_delay`       | no       | `5`                    | Seconds between checks.                                       |
| `proxmox_lxc_mount_gate_snippets_storage` | no       | `local`                | Storage the `hookscript:` line names.                         |
| `proxmox_lxc_mount_gate_snippets_dir`     | no       | `/var/lib/vz/snippets` | That storage's snippets directory on the node.                |
| `proxmox_lxc_mount_gate_hook_name`        | no       | `""`                   | Hookscript file name; empty means `lxc-mount-gate-<ctid>.sh`. |
| `proxmox_lxc_mount_gate_apply`            | no       | `false`                | Safety gate, see above.                                       |

The mount unit is passed rather than derived from the path: systemd escapes some
characters in a path (a `-` becomes `\x2d`), and the name the role uses must be
the unit that exists on the node. When another role writes the units, pass the
names it derived.

## Usage

```yaml
- hosts: pve_nodes
  become: true
  tasks:
    - name: Gate container 200 on its iSCSI-backed media mount
      ansible.builtin.include_role:
        name: richard_lynch.proxmox.proxmox_lxc_mount_gate
      vars:
        proxmox_lxc_mount_gate_ctid: 200
        proxmox_lxc_mount_gate_mount_path: /mnt/media
        proxmox_lxc_mount_gate_mount_unit: mnt-media.mount
        proxmox_lxc_mount_gate_requires_units:
          - iscsi-login@iqn.2005-10.org.example_media.service
        # Leave false to stage and review; true wires the hookscript and sets onboot: 1.
        proxmox_lxc_mount_gate_apply: false
```

To undo an apply: `pct set <ctid> --onboot 0 --delete hookscript`.

## Testing

`molecule/default/` runs offline on localhost: it runs the role with apply off
into a scratch snippets directory, checks the rendered hookscript carries the
caller's values and is valid bash, runs its pre-start phase against a path that
is not a mountpoint and requires the refusal, and runs the role once per
required option with that option left out, requiring an argument-validation
failure that names it and no file written.
