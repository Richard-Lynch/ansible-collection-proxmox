# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Install Intel VA-API userspace and prove the GPU can actually be opened",
            description=[
                "Installs a VA-API stack new enough for the target GPU and VERIFIES it by opening",
                "the device, rather than reporting success once packages are present.",
                "",
                "On an Intel Arc (Battlemage) card the xe driver can bind the card and report its full",
                "VRAM while vainfo still fails with 'va_openDriver() returns -1' because bookworm's",
                "libva (2.17) has no xe backend. That is a userspace gap, not a driver problem.",
                "",
                "Generate-don't-apply. The role refuses to act if the GPU is not bound to a host",
                "driver (e.g. still on vfio-pci), since userspace cannot help until the kernel has",
                "claimed the card.",
            ],
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "vaapi_device_id": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "PCI vendor:device of the GPU, e.g. '8086:e20c' for an Arc (Battlemage) card. Required:",
                        "the role resolves this card's OWN render node from its PCI address, because",
                        "probing /dev/dri/renderD128 would test whatever device is first — on a host",
                        "with a working iGPU that masks a completely broken discrete card.",
                    ],
                ),
                "vaapi_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "false (default) probes and reports what it would install, changing nothing.",
                        "true enables the backports suite (pinned) and installs the packages.",
                    ],
                ),
                "vaapi_packages": OptionSpec(
                    type="list",
                    elements="str",
                    required=False,
                    default=["intel-media-va-driver-non-free", "libva2", "libva-drm2", "vainfo"],
                    description=[
                        "Packages pulled from the backports suite. Named explicitly and installed",
                        "with an explicit suite suffix — never a dist-upgrade.",
                    ],
                ),
                "vaapi_backports_suite": OptionSpec(
                    type="str",
                    required=False,
                    default="bookworm-backports",
                    description=[
                        "Suite providing the newer VA-API stack. PVE 8 is bookworm-based, and",
                        "bookworm-backports carries a libva with the xe backend.",
                    ],
                ),
                "vaapi_stable_suite": OptionSpec(
                    type="str",
                    required=False,
                    default="bookworm",
                    description=["Stable suite, named in the rollback instructions."],
                ),
                "vaapi_sysfs_base": OptionSpec(
                    type="str",
                    required=False,
                    default="/sys/bus/pci/devices",
                    description=[
                        "Where PCI devices are enumerated. Overridable ONLY so the molecule scenario",
                        "can run the real role against a fixture tree; production never sets it.",
                    ],
                ),
                "vaapi_backports_filename": OptionSpec(
                    type="str",
                    required=False,
                    default="ansible-vaapi-backports",
                    description=[
                        "Basename for the sources.list.d and preferences.d files this role owns, so",
                        "both can be identified and removed together on rollback.",
                    ],
                ),
            },
        )
    }
)
