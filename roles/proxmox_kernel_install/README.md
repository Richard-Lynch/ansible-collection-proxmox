# proxmox_kernel_install

Installs an additional Proxmox kernel series **alongside** the running one, so the host can boot it
next time. Never removes a kernel, never reboots.

For example, Intel Arc (Battlemage, e.g. B570/B580) cards: kernel 6.8's `xe` and `i915` carry **no PCI alias** for
`8086:e20c` (Battlemage support landed around 6.12), so the card cannot bind on that kernel no
matter how the IOMMU groups are arranged.

## Usage

```yaml
- hosts: gpu_hosts
  gather_facts: true
  become: true
  roles:
    - role: richard_lynch.proxmox.proxmox_kernel_install
      kernel_install_package: proxmox-kernel-6.14
      kernel_install_apply: "{{ kernel_apply | default(false) }}"
```

Inputs are declared in `meta/argument_specs.py` — the `.yml` and `defaults/main.yml` are
**generated** from it.

Only a **series** name is accepted (`proxmox-kernel-6.14`), not an exact build. Pinning a build here
would stop the host receiving security updates for its own kernel.

## Safety properties

Each is asserted by `molecule/default/verify.yml`; the already-installed detection has been
mutation-tested (broken deliberately to confirm the test fails).

- **Generate-don't-apply.** The default run reports and changes nothing.
- **Never removes a kernel.** `state: present` on exactly one named package, `autoremove: false`,
  never `latest`. It cannot become an incidental full-system upgrade of a hypervisor, and it cannot
  drop the running kernel as a side effect.
- **Refuses when apt has no candidate**, rather than emitting an opaque apt error.
- **Refuses when `/boot` is nearly full.** A full `/boot` during initramfs generation can leave a
  half-written initramfs for a kernel the bootloader already references — a routine reboot then
  becomes a recovery session.
- **Verifies after installing**: re-reads dpkg, and checks every `vmlinuz-*` on `/boot` has a
  matching `initrd.img-*`. A kernel without an initramfs will not boot, and dpkg reporting success
  is a weaker statement than "there is a bootable image".
- **Exact series matching.** `proxmox-kernel-6.14` is not confused with installed
  `proxmox-kernel-6.8*` packages — a substring match would report it as already installed and
  silently skip the install the reboot depends on.
- **Idempotent.** An already-installed kernel short-circuits, even with `apply=true`.
- **Never reboots.**

## Rollback

The running kernel is never touched, so it remains installed and selectable:

```bash
# pick the previous entry in the boot menu, or pin it explicitly:
proxmox-boot-tool kernel pin 6.8.12-4-pve
```

On a GRUB host, the previous kernel appears under "Advanced options" in the
boot menu.

## What it deliberately does NOT do

- **Reboot**, or schedule one.
- **Remove, purge or autoremove** any kernel — including old ones. Cleaning up `/boot` is a
  separate decision with its own risk.
- **Upgrade anything else.** One package, `state: present`.
- **Guarantee the new kernel boots.** It verifies an image and initramfs exist; whether the
  hardware is happy on that kernel is learned by rebooting, which is why the old one is kept.

## Test coverage (honest)

`molecule/default/` runs the **real role** against fake `dpkg`/`apt-cache`/`df`/`uname` modelling
a host that runs a 6.8 kernel with 6.14 available and not installed. Genuinely
covered: state detection, exact series matching, the already-installed short-circuit, and both
refusal paths.

**Not covered, and not claimed:** the apt transaction itself, initramfs generation, and whether the
installed kernel actually boots the hardware.
