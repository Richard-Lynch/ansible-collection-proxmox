# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DEFAULT_AUTHOR = "Collection maintainers"
from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec

# Every value that names a particular guest, path or unit is REQUIRED with no default: the role
# must be right for any caller, and a default that names one host's container is right for that
# host only by coincidence. The defaults below are Proxmox VE's own (the `local` storage and its
# snippets directory) or tuning that suits any caller.
argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Gate a Proxmox LXC's start on a host mount with a pre-start hookscript",
            description=[
                "Stages a Proxmox VE hookscript that, in the pre-start phase, starts the units",
                "a host mount depends on and refuses the container start until the mount path",
                "is a real mountpoint. With apply, also enables and starts those units, wires the",
                "hookscript into the container config and sets onboot: 1.",
            ],
            version_added="1.1",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_lxc_mount_gate_ctid": OptionSpec(
                    type="int",
                    required=True,
                    min_value=100,
                    description=["The Proxmox VE id of the container whose start is gated."],
                ),
                "proxmox_lxc_mount_gate_mount_path": OptionSpec(
                    type="str",
                    required=True,
                    pattern=r"^/.+",
                    description=[
                        "Absolute host path that must be a mountpoint before the container may",
                        "start (the source of the container's bind mount).",
                    ],
                ),
                "proxmox_lxc_mount_gate_mount_unit": OptionSpec(
                    type="str",
                    required=True,
                    pattern=r".+\.mount$",
                    description=[
                        "The systemd mount unit for the mount path. The hookscript starts it, and",
                        "starts it again on each wait, until the path is mounted.",
                    ],
                ),
                "proxmox_lxc_mount_gate_requires_units": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    default=[],
                    description=[
                        "Units started, in this order, before the mount unit (for example an",
                        "iSCSI login service). With apply they are also enabled and started.",
                    ],
                ),
                "proxmox_lxc_mount_gate_wait_tries": OptionSpec(
                    type="int",
                    required=False,
                    default=30,
                    min_value=1,
                    description=[
                        "How many times the hookscript checks the mount before refusing the start."
                    ],
                ),
                "proxmox_lxc_mount_gate_wait_delay": OptionSpec(
                    type="int",
                    required=False,
                    default=5,
                    min_value=1,
                    description=["Seconds between the hookscript's checks."],
                ),
                "proxmox_lxc_mount_gate_snippets_storage": OptionSpec(
                    type="str",
                    required=False,
                    default="local",
                    description=[
                        "The Proxmox VE storage whose snippets the container config references."
                    ],
                ),
                "proxmox_lxc_mount_gate_snippets_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/var/lib/vz/snippets",
                    description=[
                        "The host directory of that storage's snippets, where the hookscript is written."
                    ],
                ),
                "proxmox_lxc_mount_gate_hook_name": OptionSpec(
                    type="str",
                    required=False,
                    default="",
                    pattern=r"^$|^[A-Za-z0-9._-]+$",
                    description=[
                        "File name of the hookscript in the snippets directory. Empty means",
                        "lxc-mount-gate-<ctid>.sh.",
                    ],
                ),
                "proxmox_lxc_mount_gate_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "Safety gate. false (default) stages the hookscript and reports what apply",
                        "would change, with no change to how the host boots. true enables and",
                        "starts the units, fails if the path is not then mounted, wires the",
                        "hookscript into the container config and sets onboot: 1.",
                    ],
                ),
            },
        )
    }
)
