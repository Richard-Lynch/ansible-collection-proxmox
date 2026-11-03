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

OPTIONS_VLAN = {
    "id": OptionSpec(
        type="int",
        required=True,
    ),
    "name": OptionSpec(
        type="str",
        required=True,
    ),
    "domain_name": OptionSpec(
        type="str",
        required=True,
        description=["FQDN"],
    ),
    "gateway": OptionSpec(
        type="str",
        required=True,
        description=["The VLAN gateway address, e.g. `192.0.2.1`"],
    ),
    "dns": OptionSpec(
        type="str",
        required=False,
        description=["The VLAN DNS server address, e.g. `192.0.2.53`"],
    ),
    "base": OptionSpec(
        type="str",
        required=True,
        description=["The VLAN network address, e.g. `192.0.2.0`"],
    ),
    "cidr": OptionSpec(
        type="int",
        required=True,
    ),
}

ARGSPEC_VLAN = OptionSpec(
    type="dict",
    required=True,
    description=[
        "The VLAN config for the primary network connection of the VM",
        "Normally one entry of a VLAN map kept in the inventory",
    ],
    options=OPTIONS_VLAN,
)

OPTIONS_STORAGE = ["local", "local-lvm"]


ARGSPEC_HOSTPCI = OptionSpec(
    type="str",
    required=False,
)

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Creates a TrueNAS VM on Proxmox and pauses for the manual install",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "truenas_vm_iso_url": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "e.g.",
                        "https://download.sys.truenas.net/TrueNAS-SCALE-Fangtooth/25.04.0/TrueNAS-SCALE-25.04.0.iso",
                    ],
                ),
                "truenas_password": OptionSpec(type="str", required=True),
                "truenas_callback_url": OptionSpec(type="str", required=True),
                "truenas_vm_vlan": ARGSPEC_VLAN,
                "truenas_vm_name": OptionSpec(
                    type="str",
                    required=True,
                ),
                "truenas_vm_id": OptionSpec(
                    type="int",
                    required=True,
                ),
                "truenas_vm_startup_order": OptionSpec(
                    type="int",
                    required=True,
                    description=[
                        "The order Proxmox should start this container relative to the others"
                    ],
                ),
                "truenas_vm_storage": OptionSpec(
                    type="str",
                    required=False,
                    default="local-lvm",
                    choices=OPTIONS_STORAGE,
                ),
                "truenas_vm_disk_size": OptionSpec(type="int", required=False, default=64),
                "truenas_vm_memory": OptionSpec(type="int", required=False, default=16384),
                "truenas_vm_cores": OptionSpec(type="int", required=False, default=4),
                "truenas_vm_bridge": OptionSpec(type="str", required=True),
                "truenas_vm_hostpci": OptionSpec(
                    type="dict",
                    required=False,
                    description=[
                        "https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_kvm_module.html#parameter-hostpci"
                    ],
                    options={f"hostpci{i}": ARGSPEC_HOSTPCI for i in range(10)},
                ),
            },
        ),
        "cleanup_boot": ArgumentSpec(
            short_description="Detaches the TrueNAS install ISO and restarts the VM",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox": ARGSPEC_PROXMOX,
                "truenas_vm_id": OptionSpec(
                    type="int",
                    required=True,
                ),
            },
        ),
    }
)
