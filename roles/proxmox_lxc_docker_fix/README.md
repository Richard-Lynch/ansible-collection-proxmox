# proxmox_lxc_docker_fix

Lets Docker run inside an **unprivileged LXC on PVE 8.x** (lxc-pve < 6.0.5) by writing two raw
`lxc.*` lines into the container's config and rebooting it once. Remove the role after the
upgrade to PVE 9 / lxc-pve >= 6.0.5-2 (https://forum.proxmox.com/threads/175437/).

```
lxc.apparmor.profile: unconfined
lxc.mount.entry: /dev/null sys/module/apparmor/parameters/enabled none bind 0 0
```

## Ownership of the lxc.* lines

These lines are owned **here and only here**. The PVE API cannot set raw `lxc.*` keys, and it
keeps them verbatim across every API config write, so `deployment_proxmox_lxc` never touches
them.

They are written with exact-line `lineinfile`, **not** a marked `blockinfile` block. PVE parses
every `#` line of a container config into the description, so block markers become description
text, the next description update drops them, and a marker-based role re-inserts its block and
reboots on every converge. The role also deletes any leftover marker lines; that changes only
the description and does not reboot.

## Inputs

See [`meta/argument_specs.yml`](meta/argument_specs.yml) (generated from
`meta/argument_specs.py`). `proxmox_lxc_docker_fix_vmid` is required;
`proxmox_lxc_docker_fix_hostname` makes the role wait for SSH after the reboot.

## Entry points

- `main`: write the lines and reboot with `pct reboot` **only** if either line changed.
- `tasks/configure.yml`: the file edits on their own, with no reboot. Molecule uses it.

## Testing

`molecule/default/` is offline. It runs two consecutive converges of a fixture shaped like a
container config that a marker-based fix loops on (`deployment_proxmox_lxc`'s `tasks/drift.yml`, a simulated PVE
PUT, then this role's `tasks/configure.yml`) and asserts that the second pass is a fixed point:
no drift, no update, no reboot, and a byte-identical file. It also checks a fresh guest with a
snapshot section, where the lines must go into the main section, once. The scenario was run
against the old blockinfile role and against the module's own tag comparison, and failed both
times.
