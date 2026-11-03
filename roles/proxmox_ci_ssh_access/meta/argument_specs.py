# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Narrow CI SSH user + restricted sudoers on a PVE node",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_ci_ssh_user": OptionSpec(
                    type="str",
                    required=True,
                    description=["The OS user the CI runner logs in as, e.g. `cistaging`."],
                ),
                "proxmox_ci_ssh_pubkey": OptionSpec(
                    type="str",
                    required=True,
                    description=["The runner's SSH public key to authorize."],
                ),
                "proxmox_ci_ssh_sudoers_file": OptionSpec(
                    type="str",
                    required=False,
                    default="/etc/sudoers.d/proxmox-ci",
                    description=["The sudoers drop-in that grants the CI user its commands."],
                ),
                "proxmox_ci_ssh_sudo_commands": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    description=["The ONLY commands the CI user may run as root (pct/qm/pvesh)."],
                ),
            },
        )
    }
)
