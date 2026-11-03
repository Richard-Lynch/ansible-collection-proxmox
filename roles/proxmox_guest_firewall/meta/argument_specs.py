# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Report, preview or apply the Proxmox firewall for a set of guests",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_guest_firewall_action": OptionSpec(
                    type="str",
                    required=False,
                    default="report",
                    choices=["report", "preview", "apply"],
                    description=[
                        "report: read the datacenter, node and guest firewall state, change nothing.",
                        "preview: report, then render the intended cluster.fw and <vmid>.fw files",
                        "and print what would change, change nothing.",
                        "apply: preview, then write. Needs proxmox_guest_firewall_apply=true too.",
                        "The FIRST apply turns the DATACENTER firewall on, which is CLUSTER-WIDE.",
                    ],
                ),
                "proxmox_guest_firewall_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "The second key for action=apply. Without it apply refuses before any",
                        "read-back or write.",
                    ],
                ),
                "proxmox_guest_firewall_datacenter_confirm": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "The THIRD key, for the cluster-wide step only. With apply but without it,",
                        "apply writes the guest files and NIC flags (inert while the datacenter is",
                        "off) and stops before cluster.fw.",
                    ],
                ),
                "proxmox_guest_firewall_nodes": OptionSpec(
                    type="list",
                    required=True,
                    elements="dict",
                    description=[
                        "Every cluster node, as {name, address}. The report reads each node's host",
                        "firewall state, and the apply before-check needs 22 and 8006 to answer on",
                        "every one of them. Derive it from the inventory.",
                    ],
                ),
                "proxmox_guest_firewall_cluster_options": OptionSpec(
                    type="dict",
                    required=False,
                    default={"enable": 1, "policy_in": "ACCEPT", "policy_out": "ACCEPT"},
                    description=[
                        "The [OPTIONS] of cluster.fw. Proxmox applies guest rules only while the",
                        "datacenter has enable=1. The default policies are ACCEPT, so switching it on",
                        "does not start filtering node traffic; only guests whose own options say",
                        "enable=1 are filtered.",
                    ],
                ),
                "proxmox_guest_firewall_ipsets": OptionSpec(
                    type="dict",
                    required=False,
                    default={},
                    description=[
                        "Cluster IPSets, as name -> list of {cidr, comment}. Rules refer to them as",
                        "+<name>. Each entry is a single address or a CIDR, never a hostname.",
                    ],
                ),
                "proxmox_guest_firewall_guests": OptionSpec(
                    type="list",
                    required=False,
                    default=[],
                    elements="dict",
                    description=[
                        "Each guest whose firewall this role owns:",
                        "  name, vmid, node, type (lxc|qemu), policy_in, policy_out (ACCEPT|DROP|REJECT)",
                        "  rules: list of {dir: in|out, action: ACCEPT|DROP|REJECT, proto, dport,",
                        "         source, dest, comment}. source and dest are a CIDR or +ipset.",
                        "Every rule needs a comment. A rule nobody can justify is a rule nobody dares",
                        "remove.",
                    ],
                ),
                "proxmox_guest_firewall_management_ports": OptionSpec(
                    type="list",
                    required=False,
                    elements="int",
                    default=[22, 8006],
                    description=[
                        "Ports that must answer on every node before AND after an apply. Losing",
                        "8006 or 22 on a node is the failure that turns a firewall change into a",
                        "console visit.",
                    ],
                ),
                "proxmox_guest_firewall_fw_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/etc/pve/firewall",
                    description=[
                        "Where Proxmox keeps cluster.fw and <vmid>.fw (pmxcfs, cluster-shared).",
                        "The molecule scenario points this at a scratch directory.",
                    ],
                ),
                "proxmox_guest_firewall_render_only": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "Skip every read of the live cluster (pvesh, pve-firewall) and only render",
                        "and gate. For the molecule scenario, which has no cluster to read.",
                    ],
                ),
            },
        ),
    }
)
