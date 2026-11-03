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

OPTIONS_STORAGE = ["local", "local-lvm"]

ARGSPEC_DEPLOYMENT_PROXMOX_VM_TEMPLATE = OptionSpec(
    description="Which VM template do you want to use?",
    type="str",  # TODO this could maybe be constrainted to the list of actual templates with choices?
    required=True,
)

ARGSPEC_DEPLOYMENT_PROXMOX_VM_CI = OptionSpec(
    description=[
        "Cloud-init settings for the clone. The login user and password have no default: a",
        "well-known default credential would be a usable login on every VM that omitted them.",
    ],
    type="dict",
    required=True,
    options={
        "user": OptionSpec(type="str", required=True),
        "password": OptionSpec(type="str", required=True, no_log=True),
        "upgrade": OptionSpec(type="bool", required=False, default=True),
    },
)

ARGSPEC_IP_CONFIG = OptionSpec(
    type="dict",
    required=False,
    description=[
        "Values allowed are - '[gw=<GatewayIPv4>] [,gw6=<GatewayIPv6>] [,ip=<IPv4Format/CIDR>] [,ip6=<IPv6Format/CIDR>]'.",
        "IP addresses use CIDR notation, gateways are optional but they should be in the same subnet of specified IP address.",
        "The special string dhcp can be used for IP addresses to use DHCP, in which case no explicit gateway should be provided.",
        "For IPv6 the special string auto can be used to use stateless autoconfiguration.",
        "If cloud-init is enabled and neither an IPv4 nor an IPv6 address is specified, it defaults to using dhcp on IPv4.",
    ],
    options={
        "ip": OptionSpec(
            type="str",
            description="<IPv4Format/CIDR>",
            required=False,
            default="dhcp",
        ),
        "gw": OptionSpec(type="str", required=False, description="<GatewayIPv4>"),
        "ip6": OptionSpec(
            type="str",
            required=False,
            description="<IPv6Format/CIDR>",
        ),
        "gw6": OptionSpec(type="str", required=False, description="<GatewayIPv6>"),
    },
)

ARGSPEC_DEPLOYMENT_PROXMOX_VM_MACHINE = OptionSpec(
    type="dict",
    required=True,
    options={
        # REQUIRED -- ID + access
        "name": OptionSpec(type="str", required=True),
        "vmid": OptionSpec(type="int", required=True),
        "ipconfig": OptionSpec(
            type="dict",
            required=False,
            description=[
                "See https://pve.proxmox.com/pve-docs/chapter-qm.html (search 'ipconfig[n]')",
                "Cloud-init: Set the IP configuration.",
                'A hash/dictionary of network IP configurations. ipconfig=\'{"key":"value", "key":"value"}\'.',
                "Keys allowed are - ipconfig[n] where 0 ≤ n ≤ network interfaces.",
            ],
            options={
                "ipconfig0": ARGSPEC_IP_CONFIG,
                "ipconfig1": ARGSPEC_IP_CONFIG,
                "ipconfig2": ARGSPEC_IP_CONFIG,
            },
        ),
        # OPTIONAL -- hardware
        "cores": OptionSpec(
            type="int",
            required=False,
            default=2,
        ),
        "memory": OptionSpec(
            type="int",
            required=False,
            default=8192,
        ),
        "size": OptionSpec(
            type="str",
            required=False,
            default="32G",
        ),
        "storage_target": OptionSpec(
            type="str",
            required=False,
            default="local-lvm",
            choices=OPTIONS_STORAGE,
        ),
        # OPTIONAL -- TAGS
        "tags": OptionSpec(type="list", elements="str", required=False, default=DEFAULT__TAGS),
    },
)

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Deploys a VM onto a Proxmox host",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "public_ssh_key": OptionSpec(type="str", required=True),
                "proxmox": ARGSPEC_PROXMOX,
                "deployment_proxmox_vm_template_name": ARGSPEC_DEPLOYMENT_PROXMOX_VM_TEMPLATE,
                "deployment_proxmox_vm_ci": ARGSPEC_DEPLOYMENT_PROXMOX_VM_CI,
                "deployment_proxmox_vm_machine": ARGSPEC_DEPLOYMENT_PROXMOX_VM_MACHINE,
            },
        ),
    }
)
