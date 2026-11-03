# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DEFAULT_AUTHOR = "Collection maintainers"
from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Create or converge one cloud-init Proxmox VM from a checksummed image",
            description=[
                "Runs ON the Proxmox node (qm and pvesh are local), so it needs no API token in the",
                "play. Downloads the cloud image once, verified against a pinned sha256; creates the",
                "VM only when its vmid is absent; on an existing VM converges memory, balloon, cores,",
                "tags, startup and description, and only GROWS the disk. It starts a stopped VM and",
                "never restarts a running one (the older deployment_proxmox_vm restarted a running VM",
                "on every converge). Refuses a vmid that exists on another node or under another name.",
                "Which node, vmid, VLAN, sizes and key are site configuration and come from",
                "inventory; the role knows how, not which. Cloud-init settings (user, key, address)",
                "apply when the VM is created; changing them later is a deliberate rebuild, not a",
                "converge.",
            ],
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "proxmox_cloud_vm_node": OptionSpec(
                    type="str",
                    required=True,
                    description=["Proxmox node name the VM lives on (pvesh /nodes/<name>)."],
                ),
                "proxmox_cloud_vm_vmid": OptionSpec(
                    type="int",
                    required=True,
                    min_value=100,
                    max_value=999999999,
                    description=[
                        "The VM's id. An existing VM with this id and another name is refused."
                    ],
                ),
                "proxmox_cloud_vm_name": OptionSpec(
                    type="str",
                    required=True,
                    pattern=r"\A[a-z0-9][a-z0-9-]{0,62}\Z",
                    description=["VM name; it is also the guest's hostname."],
                ),
                "proxmox_cloud_vm_cores": OptionSpec(
                    type="int", required=True, min_value=1, description=["vCPU count."]
                ),
                "proxmox_cloud_vm_memory_mb": OptionSpec(
                    type="int", required=True, min_value=512, description=["Memory ceiling in MB."]
                ),
                "proxmox_cloud_vm_balloon_mb": OptionSpec(
                    type="int",
                    default=0,
                    min_value=0,
                    description=[
                        "Balloon floor in MB: the host may reclaim memory down to this when it is",
                        "under pressure. 0 disables ballooning (the VM always holds its ceiling).",
                    ],
                ),
                "proxmox_cloud_vm_disk_gb": OptionSpec(
                    type="int",
                    required=True,
                    min_value=10,
                    description=["Root disk size in GB. Grown to this when smaller; never shrunk."],
                ),
                "proxmox_cloud_vm_storage": OptionSpec(
                    type="str",
                    default="local-lvm",
                    description=["Storage for the disk and the cloud-init drive."],
                ),
                "proxmox_cloud_vm_bridge": OptionSpec(
                    type="str", default="vmbr0", description=["Bridge the NIC attaches to."]
                ),
                "proxmox_cloud_vm_vlan_tag": OptionSpec(
                    type="int",
                    required=True,
                    min_value=1,
                    max_value=4094,
                    description=[
                        "VLAN tag on the NIC. Required: an untagged guest lands on the wrong network."
                    ],
                ),
                "proxmox_cloud_vm_tags": OptionSpec(
                    type="list", elements="str", default=["ansible"], description=["Proxmox tags."]
                ),
                "proxmox_cloud_vm_description": OptionSpec(
                    type="str", default="", description=["Free-text description shown in the UI."]
                ),
                "proxmox_cloud_vm_onboot": OptionSpec(
                    type="bool", default=True, description=["Start the VM when the node boots."]
                ),
                "proxmox_cloud_vm_startup_order": OptionSpec(
                    type="int",
                    default=0,
                    min_value=0,
                    description=["Boot order among guests; 0 sets no ordering."],
                ),
                "proxmox_cloud_vm_ci_user": OptionSpec(
                    type="str",
                    default="ubuntu",
                    description=["Cloud-init login user. Gets passwordless sudo from the image."],
                ),
                "proxmox_cloud_vm_ssh_public_key": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "Public key cloud-init installs for the login user. No password is set."
                    ],
                ),
                "proxmox_cloud_vm_image": OptionSpec(
                    type="dict",
                    required=True,
                    description=[
                        "The cloud image. Keys: url (https) and sha256 (64 hex). Pin a dated release",
                        "directory, never a moving alias, so the checksum stays true.",
                    ],
                ),
                "proxmox_cloud_vm_image_dir": OptionSpec(
                    type="str",
                    default="/var/lib/vz/template/iso",
                    description=["Directory on the node the image is downloaded into."],
                ),
                "proxmox_cloud_vm_snippet_storage": OptionSpec(
                    type="str",
                    default="local",
                    pattern=r"\A[A-Za-z0-9][A-Za-z0-9_-]*\Z",
                    description=[
                        "Storage whose content types include snippets, where the cloud-init",
                        "vendor-data file is written. The Ubuntu cloud image ships WITHOUT",
                        "qemu-guest-agent, so without vendor-data that installs it the agent",
                        "wait below can never succeed.",
                    ],
                ),
                "proxmox_cloud_vm_snippet_enable": OptionSpec(
                    type="bool",
                    default=False,
                    description=[
                        "Add 'snippets' to the snippet storage's content types when it lacks them",
                        "(additive; existing types are kept). Off by default because it edits",
                        "cluster-wide storage configuration; when off and missing, the role refuses.",
                    ],
                ),
                "proxmox_cloud_vm_snippet_dir": OptionSpec(
                    type="str",
                    default="/var/lib/vz/snippets",
                    description=[
                        "Directory on the node that snippet_storage serves as 'snippets'."
                    ],
                ),
                "proxmox_cloud_vm_agent_wait_seconds": OptionSpec(
                    type="int",
                    default=300,
                    min_value=30,
                    description=[
                        "How long to wait for the QEMU guest agent to answer after start."
                    ],
                ),
            },
        ),
    }
)
