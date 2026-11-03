# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

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


OPTIONS_USB = OptionSpec(
    type="dict",
    description="USB devices which should be attached to the VM",
    options={
        "host": OptionSpec(
            type="str",
            required=True,
            description=[
                "Host is either spice or the USB id/port.",
                "host=value | spice",
            ],
        ),
        "mapping": OptionSpec(
            type="str",
            required=False,
            description=["The mapped USB device name", "mapping=value"],
        ),
        "usb3": OptionSpec(
            type="int",
            required=False,
            description=["Enables USB 3 support", "usb3=1|0"],
            choices=[0, 1],
        ),
    },
)
argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Sets up a home assistant VM",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "homeassistant_vm_iso_url": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "The URL to the `.qcow2.xz` file to be installed as the VM",
                        "example: https://github.com/home-assistant/operating-system/releases/download/15.2/haos_ova-15.2.qcow2.xz",
                    ],
                ),
                "homeassistant_vm_id": OptionSpec(
                    type="int",
                    required=True,
                    description=["The Proxmox VMID for the new VM"],
                ),
                "homeassistant_vm_vlan": ARGSPEC_VLAN,
                # OPTIONAL -- startup
                "homeassistant_vm_startup_order": OptionSpec(
                    type="int",
                    required=False,
                    description=[
                        "The order Proxmox should start this container relative to the others",
                        "Will default to the VLAN ID",
                    ],
                ),
                # OPTIONAL -- network
                "homeassistant_vm_name": OptionSpec(
                    type="str",
                    required=False,
                    default="homeassistant",
                    description=["The hostname of the VM"],
                ),
                "homeassistant_vm_bridge": OptionSpec(
                    type="str",
                    required=False,
                    default="vmbr0",
                ),
                # OPTIONAL -- hardware
                "homeassistant_vm_usb": OptionSpec(
                    type="dict",
                    required=False,
                    description="https://docs.ansible.com/ansible/latest/collections/community/general/proxmox_kvm_module.html#parameter-usb",
                    options={f"usb{i}": OPTIONS_USB for i in range(0, 10)},
                ),
                "homeassistant_vm_cores": OptionSpec(
                    type="int",
                    required=False,
                    default=4,
                ),
                "homeassistant_vm_memory": OptionSpec(
                    type="int",
                    required=False,
                    default=8192,
                ),
                "homeassistant_vm_storage": OptionSpec(
                    type="str",
                    required=False,
                    default="local-lvm",
                    choices=OPTIONS_STORAGE,
                ),
                "homeassistant_vm_disk_size": OptionSpec(
                    type="str",
                    required=False,
                    default="64G",
                ),
            },
        ),
    }
)
