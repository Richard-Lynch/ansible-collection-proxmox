# deployment_proxmox_lxc

Creates or converges one Proxmox LXC from a declared container dict, starts it,
and waits until it has an inventory address and answers SSH.

## Convergence

1. **Read** the container's status and current config (`proxmox_vm_info`,
   `config: current`).
2. **Create** it only if it does not exist.
3. **Compare** the declared config with the live one (`tasks/drift.yml`, using
   the `richard_lynch.proxmox.dpl_lxc_config_drift` filter). Only declared keys are compared,
   so PVE's own additions (`hwaddr`, `type=veth`, `digest`, a mount point owned
   by another play) are not drift.
4. **Update** only when there is drift. **The update never changes a MAC.** PVE
   replaces a `netN` value wholesale and generates a new `hwaddr` when the value
   has none, so the guest takes a new DHCP lease, and anything that resolved its
   old address breaks. The update therefore omits `netif` unless an interface
   itself drifted, and when one did, every declared interface carries its live
   `hwaddr` (`richard_lynch.proxmox.dpl_lxc_update_netif`).
5. **Restart** a running guest only if the update changed a key that needs a
   restart. A change to `description`, `tags`, `onboot` or `startup` alone does
   not need one.

The role does not rely on `community.general.proxmox`'s `update: true` change
detection. That detection compares a `tags` list against PVE's `;` string, and a
`description` against PVE's newline-terminated text, so it reports a change on
every run; a role that trusted it would restart every running guest on every
converge, and the re-PUT would erase `proxmox_lxc_docker_fix`'s markers, making
that role reboot the guest again.

Raw `lxc.*` lines are not this role's concern. The API cannot set them and keeps
them across updates. `proxmox_lxc_docker_fix` owns the ones it needs.

## Inputs

See [`meta/argument_specs.yml`](meta/argument_specs.yml) (generated from
`meta/argument_specs.py`).

## Testing

`molecule/default/` is offline. It covers the multi-interface netif transform
and the drift comparison against live-shaped configs: in-sync, reordered tags, a
bool in a netif string, `onboot` absent, and real changes to tags, description,
memory, VLAN and disk. Each case checks both the reported drift and whether it
calls for a restart. The MAC cases run the role's real `tasks/drift.yml`: a
description-only drift sends no `netif`, and a VLAN change keeps the live
`hwaddr`. Verify also checks that the update task in `create.yml` takes that
netif, and runs the filters' stdlib unit tests
(`tests/unit/test_lxc_config_drift.py` under the collection root). The
fixed-point proof across both roles is in
`proxmox_lxc_docker_fix/molecule/default/`.
