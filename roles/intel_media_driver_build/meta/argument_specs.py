# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ansible_devkit.argspec.models import ArgumentSpec, ArgumentSpecs, OptionSpec
DEFAULT_AUTHOR = "Collection maintainers"

argument_specs = ArgumentSpecs(
    argument_specs={
        "main": ArgumentSpec(
            short_description="Build a patched Intel iHD VA-API driver and install it alongside the bundled one",
            description=[
                "jellyfin-ffmpeg bundles iHD 25.2.6, which SIGBUSes during vaInitialize on a",
                "small-BAR Arc GPU (intel/media-driver#1927). The fix — PR #1990, commit c3e1867d —",
                "is in no tagged release up to intel-media-26.2.4, so a source build at the fix",
                "commit is the way to get it.",
                "",
                "Builds in a throwaway Ubuntu 24.04 container matching the media container's",
                "userspace, extracts only the .so, and installs it to a SEPARATE directory. The",
                "bundled driver is never touched, so rollback is deleting a directory.",
                "",
                "Generate-don't-apply, and it refuses to declare success on a build alone: the",
                "final gate requires vainfo to actually open the GPU and return codec profiles.",
            ],
            version_added="1.0",
            author=DEFAULT_AUTHOR,
            options={
                "imd_device_id": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "PCI vendor:device of the target GPU, e.g. '8086:e20c'. Required: the role",
                        "resolves THIS card's own render node from its PCI address, because probing",
                        "the first node in /dev/dri would test the working iGPU and mask a broken",
                        "discrete card.",
                    ],
                ),
                "imd_media_driver_ref": OptionSpec(
                    type="str",
                    required=True,
                    description=[
                        "git ref of intel/media-driver to build — a commit sha for reproducibility.",
                        "Must be at or after c3e1867d (the small-BAR fix); the Dockerfile asserts",
                        "the fix is present in the checked-out tree and fails the build if not.",
                    ],
                ),
                "imd_apply": OptionSpec(
                    type="bool",
                    required=False,
                    default=False,
                    description=[
                        "false (default) probes and reports, building nothing. true builds,",
                        "installs alongside, and verifies.",
                    ],
                ),
                "imd_ctid": OptionSpec(
                    type="int",
                    required=True,
                    description=["LXC guest (vmid) running the media stack."],
                ),
                "imd_container": OptionSpec(
                    type="str",
                    required=False,
                    default="jellyfin",
                    description=[
                        "Docker container inside that guest whose driver dir is targeted."
                    ],
                ),
                "imd_gmmlib_ref": OptionSpec(
                    type="str",
                    required=False,
                    default="intel-gmmlib-22.10.1",
                    description=[
                        "GmmLib tag. media-driver requires a compatible GmmLib; see",
                        "github.com/intel/media-driver/wiki/Compatibility-with-GmmLib",
                    ],
                ),
                "imd_libva_ref": OptionSpec(
                    type="str",
                    required=False,
                    default="2.22.0",
                    description=[
                        "libva tag to build against. Matched to the version jellyfin-ffmpeg bundles",
                        "(libva.so.2.2200.0 = 2.22), so the driver links against the same API the",
                        "runtime provides.",
                    ],
                ),
                "imd_driver_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/usr/lib/jellyfin-ffmpeg/lib/dri",
                    description=["Where the BUNDLED driver lives. READ ONLY — never modified."],
                ),
                "imd_install_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/opt/ihd-patched",
                    description=[
                        "Where the PATCHED driver is installed — on the GUEST filesystem, NOT inside",
                        "the container. In the upstream jellyfin image",
                        "/usr/lib/jellyfin-ffmpeg/lib/dri is in the WRITABLE LAYER (only the",
                        "configured volumes are mounts). Installing there would be destroyed by the very",
                        "container recreate needed to set LIBVA_DRIVERS_PATH — leaving libva unable",
                        "to find any driver at all, since that variable replaces the search path.",
                        "A guest path bind-mounted via compose survives recreation and makes install",
                        "and enable one atomic change.",
                    ],
                ),
                "imd_gmmlib_target": OptionSpec(
                    type="str",
                    required=False,
                    default="/usr/lib/x86_64-linux-gnu/libigdgmm.so.12",
                    description=[
                        "Where gmmlib must appear INSIDE the container. It has to be on the linker",
                        "path, not merely beside the driver: iHD links libigdgmm.so.12 dynamically",
                        "and dlopen fails with 'cannot open shared object file' otherwise.",
                    ],
                ),
                "imd_ffmpeg_lib": OptionSpec(
                    type="str",
                    required=False,
                    default="/usr/lib/jellyfin-ffmpeg/lib",
                    description=["libva location, used as LD_LIBRARY_PATH for both probes."],
                ),
                "imd_vainfo": OptionSpec(
                    type="str",
                    required=False,
                    default="/usr/lib/jellyfin-ffmpeg/vainfo",
                    description=["vainfo binary used for the before/after probes."],
                ),
                "imd_ffmpeg": OptionSpec(
                    type="str",
                    required=False,
                    default="/usr/lib/jellyfin-ffmpeg/ffmpeg",
                    description=["ffmpeg binary used for the real-encode verification."],
                ),
                "imd_test_seconds": OptionSpec(
                    type="int",
                    required=False,
                    default=3,
                    description=[
                        "Duration of each verification encode. Short on purpose: this proves the",
                        "engine works, it is not a benchmark.",
                    ],
                ),
                "imd_build_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/tmp/ansible-ihd-build",
                    description=["Build context staging dir on the PVE host."],
                ),
                "imd_guest_build_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/tmp/ihd-build",
                    description=["Build context dir inside the guest."],
                ),
                "imd_guest_stage_dir": OptionSpec(
                    type="str",
                    required=False,
                    default="/tmp/ihd-artifact",
                    description=["Where the built .so is staged inside the guest before install."],
                ),
                "imd_image_tag": OptionSpec(
                    type="str",
                    required=False,
                    default="ansible/ihd-smallbar:latest",
                    description=["Tag for the throwaway build image."],
                ),
                "imd_sysfs_base": OptionSpec(
                    type="str",
                    required=False,
                    default="/sys/bus/pci/devices",
                    description=[
                        "Where PCI devices are enumerated. Overridable ONLY so molecule can run the",
                        "real role against a fixture tree; production never sets it.",
                    ],
                ),
                "imd_build_timeout": OptionSpec(
                    type="int",
                    required=False,
                    default=3600,
                    description=[
                        "Seconds allowed for the build. media-driver is large; 10-30 minutes is",
                        "normal for a full driver build.",
                    ],
                ),
            },
        )
    }
)
