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
            short_description="Create a least-privilege PVE user, role and API token for CI",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox": ARGSPEC_PROXMOX,
                "proxmox_ci_access_user": OptionSpec(
                    type="str",
                    required=True,
                    description=["The CI PVE user to create, e.g. `ci-staging@pve`."],
                ),
                "proxmox_ci_access_role": OptionSpec(
                    type="str",
                    required=True,
                    description=["The least-privilege role name, e.g. `CIStaging`."],
                ),
                "proxmox_ci_access_token": OptionSpec(
                    type="str",
                    required=True,
                    description=["Token name; the token id is `<user>!<token>`."],
                ),
                "proxmox_ci_access_privs": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    description=[
                        "Privileges granted to the role (guest ops + read; no host modify)."
                    ],
                ),
                "proxmox_ci_access_acl_path": OptionSpec(
                    type="str",
                    required=False,
                    default="/",
                    description=["ACL path the role is granted on."],
                ),
                "proxmox_ci_access_token_privsep": OptionSpec(
                    type="int",
                    required=False,
                    default=1,
                    choices=[0, 1],
                    description=["1 = token has its own privileges (ACL the token too)."],
                ),
                "proxmox_ci_access_secret_name": OptionSpec(
                    type="str",
                    required=False,
                    default="",
                    description=[
                        "Where the caller stores the new token secret (a secret-manager item name).",
                        "Only named in the one-time message printed when the token is created.",
                    ],
                ),
            },
        )
    }
)
