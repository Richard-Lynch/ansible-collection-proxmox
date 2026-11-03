# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

ARGSPEC_PROXMOX = OptionSpec(
    description="Common arguments required to interact with Proxmox",
    type="dict",
    required=True,
    options={
        "cluster": OptionSpec(type="str", required=True),
        "node": OptionSpec(type="str", required=True),
        "user": OptionSpec(type="str", required=True),
        "password": OptionSpec(type="str", required=True),
        "api_host": OptionSpec(type="str", required=True),
        "api_token_id": OptionSpec(type="str", required=True),
        "api_token_secret": OptionSpec(type="str", required=True),
        "is_primary": OptionSpec(type="bool", required=True),
    },
)

DEFAULT__TAGS = ["ansible"]

DEFAULT__LXC_TEMPLATE = {
    "name": "debian-12-standard_12.7-1_amd64.tar.zst",
    "storage": "local",
}

DEFAULT__LXC_CONTAINER = {
    "tags": DEFAULT__TAGS,
    "cores": 4,
    "memory_mb": 2048,
    "swap_mb": 1024,
    "storage_gb": 8,
    "storage": "local-lvm",
}

OPTIONS_STORAGE = ["local", "local-lvm"]

ARGSPEC_DEPLOYMENT_PROXMOX_LXC_TEMPLATE = OptionSpec(
    description="The configuration for the LXC template to use",
    type="dict",
    required=False,
    default=DEFAULT__LXC_TEMPLATE,
    options={
        "name": OptionSpec(
            type="str",
            required=False,
            default=DEFAULT__LXC_TEMPLATE["name"],
        ),
        "storage": OptionSpec(
            type="str",
            required=False,
            default=DEFAULT__LXC_TEMPLATE["storage"],
            choices=OPTIONS_STORAGE,
        ),
    },
)

ARGSPEC_LXC_NETIF = OptionSpec(
    type="dict",
    required=False,
    options={
        "name": OptionSpec(
            type="str",
            required=True,
            description=[
                "name=<string>",
                "Name of the network device as seen from inside the container. (lxc.network.name)",
            ],
        ),
        "bridge": OptionSpec(
            type="str",
            required=True,
            description=[
                "bridge=<bridge>",
                "Bridge to attach the network device to.",
            ],
        ),
        "firewall": OptionSpec(
            type="bool",
            required=False,
            description=[
                "firewall=<boolean>",
                "Controls whether this interface's firewall rules should be used.",
            ],
        ),
        "gw": OptionSpec(
            type="str",
            required=False,
            description=[
                "gw=<GatewayIPv4>",
                "Default gateway for IPv4 traffic.",
            ],
        ),
        "gw6": OptionSpec(
            type="str",
            required=False,
            description=[
                "gw6=<GatewayIPv6>",
                "Default gateway for IPv6 traffic.",
            ],
        ),
        "hwaddr": OptionSpec(
            type="str",
            required=False,
            description=[
                "hwaddr=<XX:XX:XX:XX:XX:XX>",
                "A common MAC address with the I/G (Individual/Group) bit not set.",
            ],
        ),
        "ip": OptionSpec(
            type="str",
            required=True,
            description=[
                "ip=<(IPv4/CIDR|dhcp|manual)>",
                "IPv4 address in CIDR format.",
            ],
        ),
        "ip6": OptionSpec(
            type="str",
            required=False,
            description=[
                "ip6=<(IPv6/CIDR|auto|dhcp|manual)>",
                "IPv6 address in CIDR format.",
            ],
        ),
        "link_down": OptionSpec(
            type="bool",
            required=False,
            description=[
                "link_down=<boolean>",
                "Whether this interface should be disconnected (like pulling the plug).",
            ],
        ),
        "mtu": OptionSpec(
            type="int",
            required=False,
            description=[
                "mtu=<integer> (64 - 65535)",
                "Maximum transfer unit of the interface. (lxc.network.mtu)",
            ],
        ),
        "rate": OptionSpec(
            type="int",
            required=False,
            description=[
                "rate=<mbps>",
                "Apply rate limiting to the interface.",
            ],
        ),
        "tag": OptionSpec(
            type="int",
            required=False,
            description=[
                "tag=<integer> (1 - 4094)",
                "VLAN tag for this interface.",
            ],
        ),
        "trunks": OptionSpec(
            type="str",
            required=False,
            description=[
                "trunks=<vlanid[;vlanid...]>",
                "VLAN ids to pass through the interface",
            ],
        ),
        "type": OptionSpec(
            type="str",
            required=False,
            description=[
                "type=<veth>",
                "Network interface type.",
            ],
        ),
    },
)

ARGSPEC_DEPLOYMENT_PROXMOX_LXC_CONTAINER = OptionSpec(
    description="The configuration for the LXC container to be created",
    type="dict",
    required=False,
    options={
        # REQUIRED -- ID + access
        "vmid": OptionSpec(type="str", required=True),
        "hostname": OptionSpec(type="str", required=True),
        "description": OptionSpec(type="str", required=True),
        "user": OptionSpec(type="str", required=True),
        "password": OptionSpec(type="str", required=True),
        # TODO move these into a proper nested "netif"
        "netif": OptionSpec(
            type="dict",
            required=False,
            description=["https://pve.proxmox.com/pve-docs/chapter-pct.html#pct_container_network"],
            options={
                "net0": ARGSPEC_LXC_NETIF,
                "net1": ARGSPEC_LXC_NETIF,
                "net2": ARGSPEC_LXC_NETIF,
                "net3": ARGSPEC_LXC_NETIF,
                "net4": ARGSPEC_LXC_NETIF,
                "net5": ARGSPEC_LXC_NETIF,
                "net6": ARGSPEC_LXC_NETIF,
                "net7": ARGSPEC_LXC_NETIF,
                "net8": ARGSPEC_LXC_NETIF,
                "net9": ARGSPEC_LXC_NETIF,
            },
        ),
        # OPTIONAL -- Startup
        "onboot": OptionSpec(
            type="bool",
            required=False,
            default=False,
            description=["Specifies whether a VM will be started during system bootup."],
        ),
        "startup": OptionSpec(
            type="dict",
            required=False,
            description=[
                "Controls the order of the startup",
                "https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_module.html#parameter-startup",
                "Use order=# where # is a non-negative number to define the general startup order. Shutdown in done with reverse ordering.",
                "Use up=# where # is in seconds, to specify a delay to wait before the next VM is started.",
                "Use down=# where # is in seconds, to specify a delay to wait before the next VM is stopped.",
            ],
            options={
                "order": OptionSpec(
                    type="int",
                    required=False,
                    description="non-negative number to define the general startup order. Shutdown in done with reverse ordering.",
                ),
                "up": OptionSpec(
                    type="int",
                    required=False,
                    description="seconds, to specify a delay to wait before the next VM is started.",
                ),
                "down": OptionSpec(
                    type="int",
                    required=False,
                    description="seconds, to specify a delay to wait before the next VM is stopped.",
                ),
            },
        ),
        # FEATURES
        "features": OptionSpec(
            type="dict",
            required=True,
            description=[
                "See https://pve.proxmox.com/wiki/Linux_Container",
                "features: [force_rw_sys=<1|0>] [,fuse=<1|0>] [,keyctl=<1|0>] [,mknod=<1|0>] [,mount=<fstype;fstype;...>] [,nesting=<1|0>]",
            ],
            options={
                "force_rw_sys": OptionSpec(type="int", required=False, choices=[0, 1]),
                "fuse": OptionSpec(type="int", required=False, choices=[0, 1]),
                "keyctl": OptionSpec(type="int", required=False, choices=[0, 1]),
                "mknod": OptionSpec(type="int", required=False, choices=[0, 1]),
                "nesting": OptionSpec(type="int", required=False, choices=[0, 1]),
                "mount": OptionSpec(type="str", required=False),
            },
        ),
        # OPTIONAL -- hardware
        "cores": OptionSpec(
            type="int",
            required=False,
            default=DEFAULT__LXC_CONTAINER["cores"],
        ),
        "memory_mb": OptionSpec(
            type="int",
            required=False,
            default=DEFAULT__LXC_CONTAINER["memory_mb"],
        ),
        "swap_mb": OptionSpec(
            type="int",
            required=False,
            default=DEFAULT__LXC_CONTAINER["swap_mb"],
        ),
        "storage_gb": OptionSpec(
            type="int",
            required=False,
            default=DEFAULT__LXC_CONTAINER["storage_gb"],
        ),
        "storage": OptionSpec(
            type="str",
            required=False,
            default=DEFAULT__LXC_CONTAINER["storage"],
            choices=OPTIONS_STORAGE,
        ),
        # TAGS
        "tags": OptionSpec(type="list", elements="str", required=False, default=DEFAULT__TAGS),
    },
)

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Deploys an LXC container onto a Proxmox host",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "public_ssh_key": OptionSpec(type="str", required=True),
                # These drive the post-create wait for a new guest to appear in the dynamic
                # inventory with an address. Declared here so they have real defaults and the
                # resolver binds them before the wait loop and its failure message read them.
                "utils_verify_connection_retries": OptionSpec(
                    type="int",
                    required=False,
                    default=10,
                    min_value=1,
                    max_value=60,
                    description=[
                        "How many times to refresh the dynamic inventory waiting for a newly",
                        "created guest to appear with an address. A fresh LXC must boot and take a",
                        "DHCP lease, so this is seconds-to-a-minute territory.",
                    ],
                ),
                "utils_verify_connection_delay": OptionSpec(
                    type="int",
                    required=False,
                    default=5,
                    min_value=1,
                    max_value=60,
                    description=["Seconds to pause between inventory refresh attempts."],
                ),
                "proxmox": ARGSPEC_PROXMOX,
                "deployment_proxmox_lxc_template": ARGSPEC_DEPLOYMENT_PROXMOX_LXC_TEMPLATE,
                "deployment_proxmox_lxc_container": ARGSPEC_DEPLOYMENT_PROXMOX_LXC_CONTAINER,
            },
        ),
    }
)
