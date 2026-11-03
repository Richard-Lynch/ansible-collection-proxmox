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

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Create a template LXC in Proxmox",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "public_ssh_key": OptionSpec(type="str", required=True),
                "proxmox": ARGSPEC_PROXMOX,
                "proxmox_template_lxc_name": OptionSpec(
                    type="str",
                    required=True,
                ),
                "proxmox_template_lxc_storage": OptionSpec(
                    type="str", required=False, default="local", choices=["local"]
                ),
            },
        ),
        "cleanup": ArgumentSpec(
            short_description="Remove the downloaded template",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox": ARGSPEC_PROXMOX,
                "proxmox_template_lxc_name": OptionSpec(
                    type="str",
                    required=True,
                ),
            },
        ),
    }
)
