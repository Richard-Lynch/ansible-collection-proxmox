# intel_media_driver_build

Builds a patched Intel **iHD** VA-API driver from source and installs it **alongside** the bundled
one — proving it works before anything switches over.

## Why this exists

`jellyfin-ffmpeg` bundles iHD **25.2.6**, which **SIGBUSes during `vaInitialize`** on a small-BAR
Arc GPU. Root cause ([intel/media-driver#1927](https://github.com/intel/media-driver/issues/1927)):
`mos_bo_alloc_xe()` allocated VRAM buffers without checking whether the CPU-visible aperture is
smaller than total VRAM. The kernel then places them in the part of VRAM with no CPU mapping; iHD
`mmap`s and `memset()`s them, and the CPU faults — a valid mapping over invalid physical backing,
which is **SIGBUS rather than SIGSEGV**.

Fixed by [PR #1990](https://github.com/intel/media-driver/pull/1990) (`c3e1867d`): detect small BAR, set
`DRM_XE_GEM_CREATE_FLAG_NEEDS_VISIBLE_VRAM`, fall back to system RAM. **The fix is in no tagged
release up to `intel-media-26.2.4`**, so a source build at the fix commit is the way to get it.
The fix works without ReBAR.

## How it works

1. Builds libva → GmmLib → media-driver in a **throwaway Ubuntu 24.04 container**, matching the
   userspace of the upstream Jellyfin image. A Debian-bookworm build would link against the wrong
   `libstdc++` and fail at *load* time rather than build time — a nasty trap.
2. Extracts **only** `iHD_drv_video.so` (final stage is `FROM scratch`), plus provenance files
   recording the exact commits built.
3. Installs it to **`/opt/ihd-patched/` on the guest filesystem** — deliberately *not* inside the
   container. In the upstream Jellyfin image `/usr/lib/...` is part of the container's **writable
   layer** (only the configured volumes are mounts), so installing there would be destroyed by
   the very container recreate needed to set `LIBVA_DRIVERS_PATH` — leaving libva unable to find
   *any* driver, since that variable replaces the search path rather than extending it. A guest
   path bind-mounted via compose survives recreation and makes install-and-enable one atomic change.
4. Probes `vainfo` **before and after** and gates on the result. The "after" probe runs in a
   **throwaway container** off the same image with the driver bind-mounted read-only — so the
   running Jellyfin container is never modified or restarted.
5. Ships the **gmmlib it was built against** alongside the driver, because `iHD_drv_video.so` links
   `libigdgmm.so.12` dynamically and would otherwise resolve the container's older bundled copy.

## Usage

```yaml
- hosts: gpu_hosts
  gather_facts: true
  become: true
  roles:
    - role: richard_lynch.proxmox.intel_media_driver_build
      imd_ctid: 101                                               # example: the guest running the media container
      imd_device_id: "8086:e20c"                                  # an Arc (Battlemage) card
      imd_media_driver_ref: "c3e1867d6de236102951ee40a75319dbf54beb79"
      imd_apply: "{{ build_apply | default(false) }}"
```

Inputs are declared in `meta/argument_specs.py` — the `.yml` and `defaults/main.yml` are
**generated**.

## Safety properties

Asserted by `molecule/default/verify.yml`; the render-node selection is mutation-tested.

- **Generate-don't-apply.** Default run probes and reports, building nothing.
- **Refuses if the GPU is not claimed by a host driver** (e.g. still on `vfio-pci`) — building
  userspace cannot help until the kernel binds the card, and doing so anyway would produce a
  confusing "still broken" result whose real cause is a layer down.
- **Probes the GPU's OWN render node**, resolved from its PCI address. On a host with an
  integrated GPU (`renderD128`) and a discrete Arc (`renderD129`), probing the first node would test the iGPU, find it
  healthy, and report a completely broken Arc as fine. Mutation-tested.
- **Never touches the bundled driver.** That separation *is* the rollback.
- **Build-time gate**: the Dockerfile greps the checked-out tree for `NEEDS_VISIBLE_VRAM` and
  `has_small_bar` and fails the build if absent — so a ref predating the fix cannot silently
  produce a driver that crashes exactly as before.
- **Pinned refs**, not `master`. A floating build is not reproducible, and "which code is running
  on the GPU" must stay answerable.
- **Outcome gate**: asserts `vainfo` actually opens the device *and* returns profiles. "It
  compiled" is not the deliverable.
- **Does not enable it.** Installing and *using* are separate steps; the role reports the env var
  to set, it does not set it.

## Rollback

Remove `imd_install_dir` (default `/opt/ihd-patched`) from the guest, once nothing uses it.
Write that removal as a play of its own, and make it **refuse** while the container still
references the directory (via `LIBVA_DRIVERS_PATH` or a bind mount): removing it then would leave
libva with no driver at all — worse than never installing it.

The bundled driver is untouched throughout, so there is nothing to restore.

## What it deliberately does NOT do

- **Modify the bundled driver**, or Jellyfin's configuration.
- **Enable the patched driver** — that is a separate, deliberate decision.
- **Install a compiler anywhere persistent.** The toolchain lives and dies in the build container.
- **Restart Jellyfin.** No running transcode is disturbed.

## Test coverage (honest)

`molecule/default/` runs the **real role** against fake `lspci`/`pct` modelling the failing case
(Arc on `xe` with `renderD129`, bundled `vainfo` printing the exact `Bus error` output). Genuinely
covered: device/node resolution, the broken-driver detection, the vfio refusal, and the
dry-run-changes-nothing guarantee.

**Not covered, and not claimed:** the docker build itself (needs a real toolchain and ~20 minutes),
artifact extraction, and whether the patched driver actually fixes the GPU. That last one only a run on
real hardware answers.
