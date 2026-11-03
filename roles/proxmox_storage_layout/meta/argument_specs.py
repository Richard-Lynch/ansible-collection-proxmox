# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Dedicated PVE backup Directory storage on a thin LV (off the root LV)",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_storage_layout_vg": OptionSpec(
                    type="str",
                    required=False,
                    default="pve",
                    description=["LVM volume group."],
                ),
                "proxmox_storage_layout_thinpool": OptionSpec(
                    type="str",
                    required=False,
                    default="data",
                    description=["Thin pool to carve the backup LV from."],
                ),
                "proxmox_storage_layout_backup_lv": OptionSpec(
                    type="str",
                    required=False,
                    default="vzbackup",
                    description=["Name of the dedicated backup thin LV."],
                ),
                "proxmox_storage_layout_backup_size": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "Virtual size of the backup LV (thin-provisioned), e.g. `200G`. Sized to the",
                        "node's thin pool, so the caller declares it.",
                    ],
                ),
                "proxmox_storage_layout_backup_fstype": OptionSpec(
                    type="str",
                    required=False,
                    default="ext4",
                    description=["Filesystem for the backup LV."],
                ),
                "proxmox_storage_layout_backup_mount": OptionSpec(
                    type="str",
                    required=False,
                    default="/var/lib/vz-backups",
                    description=["Mount point for the backup volume."],
                ),
                "proxmox_storage_layout_pve_storage_id": OptionSpec(
                    type="str",
                    required=False,
                    default="local-backups",
                    description=["PVE Directory storage id to register."],
                ),
                "proxmox_storage_layout_pve_content": OptionSpec(
                    type="str",
                    required=False,
                    default="backup,iso,vztmpl",
                    description=["Content types for the storage."],
                ),
                "proxmox_storage_layout_pve_nodes": OptionSpec(
                    type="str",
                    required=False,
                    description=[
                        "Node(s) the storage is available on, comma-separated (the thin LV is",
                        "node-local). Derived from proxmox_storage_layout_backup_nodes.",
                    ],
                ),
                "proxmox_storage_layout_backup_nodes": OptionSpec(
                    type="list",
                    elements="str",
                    required=True,
                    description=[
                        "Every node that has (or will have) the backup LV mounted. The storage is",
                        "advertised on all of them, so a cluster-wide vzdump job can write on every",
                        "node; listing only the node running the role makes every other node's",
                        "guests fail to back up.",
                    ],
                ),
                "proxmox_storage_layout_prune": OptionSpec(
                    type="str",
                    required=False,
                    default="keep-daily=3,keep-weekly=2,keep-monthly=1",
                    description=["Storage-level prune-backups policy."],
                ),
            },
        )
    }
)
