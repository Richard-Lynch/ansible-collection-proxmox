# proxmox_guest_firewall

Reports, previews or applies the Proxmox VE firewall for a declared set of guests: the datacenter
`cluster.fw` (options + IPSets) and one `<vmid>.fw` per guest (options + rules). Inputs are data:
the caller declares the nodes, IPSets and guests (see `meta/argument_specs.yml`).

## Actions

| action | does | writes |
|---|---|---|
| `report` (default) | datacenter options, IPSets and rules; `local_network`; quorum; every node's host firewall options; 22/8006 on every node from the controller; each guest's options, rule count and NICs | nothing |
| `preview` | report, then renders the files and lists, per file, the lines that would be added and removed; names guests whose rules would be INERT (no `firewall=1` NIC) | nothing |
| `apply` + `proxmox_guest_firewall_apply=true` | before-checks (22/8006 on every node, quorate, the live `cluster.fw` holds no section the role would delete), then writes each `<vmid>.fw` and sets `firewall=1` on each guest NIC lacking it | guest files, NIC flags |
| ... + `proxmox_guest_firewall_datacenter_confirm=true` | writes `cluster.fw` (the **cluster-wide** switch), waits for pve-firewall, re-checks 22/8006 on every node and quorum, and **switches the datacenter back off** if any AFTER check fails | `cluster.fw` |

## Why the datacenter switch is its own key

Proxmox applies no guest rule while the datacenter firewall is off, and turning it on starts
pve-firewall's filtering on **every node**. The role therefore refuses a datacenter `policy_in` or
`policy_out` other than ACCEPT (it manages no node rules, and a DROP policy would bet 22/8006 on
`local_network` auto-detection), and writes guest files first so they are already in place,
inert, when the switch happens.

## Gates (all proven by the molecule scenario)

apply without its second key; datacenter `enable` not 1 (rules inert); a DROP/REJECT datacenter
policy; an IPSet entry that is not an IP/CIDR; a rule with no comment (or a `#` in it); a rule
naming an undeclared `+ipset`; a DROP-by-default guest with no `in -source +management -dport 22`
(Ansible lockout); a guest type other than lxc/qemu; a duplicated vmid; and, live, a guest whose
declared node/type disagrees with `/cluster/resources`.

## Known limits

- `cluster.fw` is written whole. Content in it that the role does not render (rules, aliases,
  groups, other IPSets) makes apply refuse rather than delete it.
- The rules hold addresses, so a DHCP renumber silently points a rule at an old address. Give the
  guests a DHCP reservation (or a static address) before relying on address-based rules.
- Setting `firewall=1` on an LXC NIC re-plugs it (a short network blip for that guest).
