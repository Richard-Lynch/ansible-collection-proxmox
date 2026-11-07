# Copyright: (c) 2026, Richard Lynch
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""get_best_proxmox_ip: the address to reach a Proxmox guest by, from the API inventory's facts.

Moved here from the IaaC hub's ``my.utils`` (M6 batch 5). The ``ansible.utils`` argspec validator
the original used is gone: the two options are validated here, so the collection takes no new
dependency for one filter.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress

from ansible.errors import AnsibleFilterError

DOCUMENTATION = r"""
name: get_best_proxmox_ip
short_description: Pick the address to reach a Proxmox guest by
version_added: "1.3.0"
author: Richard Lynch (@Richard-Lynch)
description:
  - From the facts the C(community.general.proxmox) inventory records for a guest, return the
    first address inside O(subnet). An LXC's C(proxmox_lxc_interfaces) is tried before its
    C(proxmox_net0); a QEMU guest's C(proxmox_lxc_interfaces), then the agent's
    C(proxmox_agent_interfaces), then C(proxmox_ipconfig0).
  - Returns V(none) when no address inside the subnet is known, so a play can tell "unknown"
    from an address.
options:
  _input:
    description: The guest's hostvars (the inventory plugin's C(proxmox_*) facts).
    type: dict
    required: true
  subnet:
    description:
      - Only addresses inside this network qualify. Required, and estate data: name your guest
        network from inventory (THE THIRD RULE), never a default baked into a public filter.
    type: str
    required: true
"""

EXAMPLES = r"""
# proxmox_guest_subnet comes from inventory (group_vars), never from the filter
ansible_host: "{{ hostvars[inventory_hostname] | richard_lynch.proxmox.get_best_proxmox_ip(subnet=proxmox_guest_subnet) }}"
"""

RETURN = r"""
_value:
  description: The first qualifying address as a string, or V(none).
  type: str
"""


def get_best_proxmox_ip(value, subnet):
    if not isinstance(value, dict):
        raise AnsibleFilterError(
            "get_best_proxmox_ip: expected the guest's hostvars (a dict), got %s"
            % type(value).__name__
        )
    try:
        net = ipaddress.ip_network(subnet)
    except ValueError as exc:
        raise AnsibleFilterError(
            "get_best_proxmox_ip: subnet %r is not a network: %s" % (subnet, exc)
        )
    ips = []

    def add_ip(ip):
        try:
            if ip:
                cleaned = ipaddress.ip_interface(ip).ip
                if cleaned in net:
                    ips.append(cleaned)
        except ValueError:
            pass  # 'dhcp', an empty string, a MAC: not an address

    vmtype = str(value.get("proxmox_vmtype") or "").lower()
    if vmtype == "lxc":
        for iface in value.get("proxmox_lxc_interfaces") or []:
            add_ip((iface or {}).get("inet"))
        net0 = value.get("proxmox_net0")
        if net0:
            add_ip(net0.get("ip"))
    elif vmtype == "qemu":
        for iface in value.get("proxmox_lxc_interfaces") or []:
            add_ip((iface or {}).get("inet"))
        for iface in value.get("proxmox_agent_interfaces") or []:
            for ip in (iface or {}).get("ip-addresses") or []:
                add_ip(ip)
        ipconf = value.get("proxmox_ipconfig0")
        if ipconf:
            add_ip(ipconf.get("ip"))
    return str(ips[0]) if ips else None


class FilterModule(object):
    def filters(self):
        return {"get_best_proxmox_ip": get_best_proxmox_ip}
