# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Free a GPU from vfio-pci on a Proxmox host so the host driver can bind it",
            description=[
                "Adds an ACS override to the kernel cmdline so a GPU that shares an IOMMU group",
                "with a device passed through to a VM can be claimed by the host's own driver",
                "(xe/i915/amdgpu) instead of vfio-pci, and installs the firmware/userspace that",
                "driver needs.",
                "",
                "Generate-don't-apply: the default run reports the diff and writes nothing.",
                "Set gpu_passthrough_apply=true to write. The role NEVER reboots (the change only",
                "takes effect at the next boot) and NEVER edits the vfio-pci ids= line, whose other",
                "entries are typically passed through to running VMs.",
                "",
                "Every file it writes is backed up to <file>.bak-<timestamp>, and the exact",
                "rollback command is printed after applying.",
            ],
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "gpu_passthrough_device_id": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "PCI vendor:device of the GPU to free, e.g. '8086:e20c' for an Intel Arc",
                        "(Battlemage) card. Required and never defaulted: the role must not guess which card to",
                        "act on. Matched against lspci; the role fails if no such display device",
                        "is present.",
                    ],
                ),
                "gpu_passthrough_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "false (default) reports the planned cmdline change and writes nothing.",
                        "true writes the cmdline, refreshes the bootloader and installs packages.",
                        "A reboot is still required afterwards and is never performed here.",
                    ],
                ),
                "gpu_passthrough_cmdline_tokens": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    default=["pcie_acs_override=downstream,multifunction"],
                    description=[
                        "Kernel cmdline tokens to ADD. Merged as a union with the existing line —",
                        "the current cmdline is never rewritten wholesale, which also makes the",
                        "role idempotent.",
                        "pcie_acs_override weakens PCIe isolation between devices that shared an",
                        "IOMMU group; it is the deliberate trade-off that makes host use of the GPU",
                        "possible, and is listed here so the choice is visible in inventory.",
                    ],
                ),
                "gpu_passthrough_vfio_conf": OptionSpec(
                    type="str",
                    required=False,
                    default="/etc/modprobe.d/vfio-pci.conf",
                    description=[
                        "Path to vfio-pci's by-ID binding config. READ ONLY: the role asserts the",
                        "GPU is not listed there and stops if it is, but never edits the file.",
                    ],
                ),
                "gpu_passthrough_install_packages": OptionSpec(
                    type="bool",
                    required=False,
                    default=True,
                    description=[
                        "Install gpu_passthrough_packages (firmware + VA-API userspace).",
                    ],
                ),
                "gpu_passthrough_require_driver": OptionSpec(
                    type="bool",
                    required=False,
                    default=True,
                    description=[
                        "Refuse to proceed unless some driver on the RUNNING kernel actually carries",
                        "a PCI alias for gpu_passthrough_device_id.",
                        "",
                        "This is the check that decides whether the change is worth a reboot at all.",
                        "Example: PVE 8's 6.8 kernels ship xe.ko but neither xe nor",
                        "i915 has an alias for 8086:e20c (Battlemage support arrives ~6.12), so",
                        "freeing the card from vfio-pci would bind nothing — a result",
                        "indistinguishable afterwards from the ACS override having failed.",
                        "",
                        "Set false ONLY to deliberately stage the cmdline change ahead of a kernel",
                        "upgrade; the role then warns loudly instead of failing.",
                    ],
                ),
                "gpu_passthrough_driver_modules": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    default=["xe", "i915", "amdgpu", "nouveau"],
                    description=[
                        "Kernel modules whose PCI aliases are searched for the target device id.",
                    ],
                ),
                "gpu_passthrough_packages": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    default=[
                        "vainfo",
                        "pciutils",
                    ],
                    description=[
                        "Userspace tooling for inspecting the GPU. Deliberately MINIMAL.",
                        "",
                        "firmware-misc-nonfree must NOT be listed here on a Proxmox host: pve-firmware",
                        "declares Conflicts/Replaces against it, so apt would propose REMOVING",
                        "pve-firmware — immediately before a planned reboot. It is also unnecessary:",
                        "pve-firmware already ships the Battlemage blobs",
                        "(/lib/firmware/xe/bmg_guc_70.bin is owned by pve-firmware).",
                        "",
                        "intel-media-va-driver-non-free is likewise omitted: bookworm's version has no",
                        "Battlemage support, and it needs the non-free component enabled, which is not",
                        "guaranteed on a PVE host. Add it deliberately per-host if wanted.",
                    ],
                ),
            },
        )
    }
)
