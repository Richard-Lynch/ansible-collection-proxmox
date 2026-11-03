# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Install an additional Proxmox kernel series alongside the running one",
            description=[
                "Adds a kernel package (e.g. proxmox-kernel-6.14) to a PVE host so it can be booted",
                "next time. Used to reach hardware support the running kernel lacks — for example,",
                "Intel Arc (Battlemage) cards need ~6.12+ for xe to recognise them.",
                "",
                "Generate-don't-apply: the default run reports what it would install and changes",
                "nothing. The role NEVER removes a kernel and NEVER reboots: the running kernel",
                "stays installed and selectable in the boot menu, which is the rollback.",
                "",
                "It installs exactly the one named package with state: present (never `latest`,",
                "never autoremove), so it cannot turn into an incidental full-system upgrade of a",
                "hypervisor or drop an existing kernel as a side effect.",
            ],
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "kernel_install_package": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "Kernel package to install, e.g. 'proxmox-kernel-6.14'. Required and never",
                        "defaulted — which kernel a hypervisor runs is not a thing to guess at.",
                        "The role fails if apt has no candidate for it.",
                    ],
                ),
                "kernel_install_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "false (default) reports the planned install and changes nothing.",
                        "true installs the package. A reboot is still required afterwards and is",
                        "never performed here.",
                    ],
                ),
                "kernel_install_min_free_mb": OptionSpec(
                    type="int",
                    required=False,
                    default=1024,
                    description=[
                        "Minimum free megabytes required on /boot before installing. A full /boot",
                        "during initramfs generation can leave a half-written initramfs for a kernel",
                        "the bootloader already references — a routine reboot then becomes a",
                        "recovery session.",
                    ],
                ),
            },
        )
    }
)
