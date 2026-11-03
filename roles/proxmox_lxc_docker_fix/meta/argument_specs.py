# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Let Docker run in an unprivileged LXC on PVE 8.x (AppArmor workaround)",
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_lxc_docker_fix_vmid": OptionSpec(
                    type="str",
                    required=True,
                    description="The container whose config gets the lxc.* AppArmor lines.",
                ),
                "proxmox_lxc_docker_fix_hostname": OptionSpec(
                    type="str",
                    required=False,
                    default="",
                    description=[
                        "Inventory name of the container. When set, the role waits for its SSH",
                        "after a reboot; when empty, it does not wait.",
                    ],
                ),
                "proxmox_lxc_docker_fix_conf_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/etc/pve/lxc",
                    description=[
                        "Directory holding <vmid>.conf. PVE's own path on every node; only a",
                        "test points it elsewhere.",
                    ],
                ),
            },
        ),
    }
)
