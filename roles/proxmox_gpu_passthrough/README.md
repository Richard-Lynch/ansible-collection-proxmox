# proxmox_gpu_passthrough

Frees a GPU from `vfio-pci` on a Proxmox host so the host's own driver (`xe`/`i915`/`amdgpu`) can
bind it, by adding an ACS override to the kernel cmdline — and installs the userspace tooling
needed to inspect it.

For a GPU — for example an Intel Arc (Battlemage, e.g. B570/B580) card — that shares an IOMMU group
with another device passed through to a VM.

## The problem it solves

A GPU can be claimed by `vfio-pci` **without being listed in `vfio-pci`'s `ids=`**, because vfio
binds at **IOMMU group** granularity. A typical case: a GPU at `<gpu-address>` shares an IOMMU
group with a device (`<vendor:device>`) passed through to a VM. The kernel log shows the
sequence:

```
vfio_pci: add [<vendor:device>...]   <- boot: the passed-through device registered by id
vfio-pci <gpu-address>: vgaarb...    <- later: the VM starts and the whole group is claimed
```

`pcie_acs_override=downstream,multifunction` makes the kernel treat PCIe downstream ports as
isolated, splitting the group so the host keeps the GPU and the VM keeps its device.

**This is a deliberate trade-off, not a free win.** ACS override asserts isolation the hardware does
not advertise; a malicious or buggy passed-through device could in principle DMA to another device
that was in the original group. When the passed-through guest is trusted this is a common choice,
but it should be made knowingly — which is why the token is spelled out in
`gpu_passthrough_cmdline_tokens` rather than hidden in the role body.

## What it does

| Concern | File | Behaviour |
|---|---|---|
| ACS override / IOMMU tokens | `/etc/default/grub` **or** `/etc/kernel/cmdline` | appends only missing tokens, preserving order |
| Bootloader | — | `update-grub` or `proxmox-boot-tool refresh` after a successful write |
| Inspection tooling | apt | `vainfo`, `pciutils` |

**Both bootloaders are supported**, detected at runtime. On GRUB only the value inside
`GRUB_CMDLINE_LINUX_DEFAULT="…"` is edited; every other setting in the file is left alone. A host
where `proxmox-boot-tool` reports no boot-uuids is a GRUB host.

**`firmware-misc-nonfree` is deliberately NOT installed.** `pve-firmware` declares
`Conflicts`/`Replaces` against it, so apt would propose removing `pve-firmware` on a hypervisor
right before a planned reboot — and it is redundant anyway, since `pve-firmware` already ships the
Battlemage blobs.

## Usage

```yaml
- hosts: gpu_hosts
  gather_facts: true          # REQUIRED — see below
  become: true
  roles:
    - role: richard_lynch.proxmox.proxmox_gpu_passthrough
      gpu_passthrough_device_id: "8086:e20c"      # an Arc (Battlemage) card
      gpu_passthrough_apply: "{{ gpu_apply | default(false) }}"
```

Inputs are declared in `meta/argument_specs.py` (the `.yml` and `defaults/main.yml` are
**generated** from it).

`gather_facts: true` is required and asserted: the backup filename uses
`ansible_facts.date_time`, and without it every run would reuse one backup path, letting a second
apply overwrite the only copy of the original cmdline.

## Safety properties

Each of these is asserted by `molecule/default/verify.yml`, and each has been mutation-tested
(the guard was deliberately broken to confirm the test fails):

- **Generate-don't-apply.** `gpu_passthrough_apply=false` (the default) writes nothing at all. Safe
  to run against a live hypervisor to see the diff. A dry run shows which bootloader path the
  role detected before anything is written.
- **Never rewrites the cmdline.** Only genuinely-absent tokens are appended, and the operator's
  original token order is preserved. A rewrite-from-template is how a host loses `root=` and stops
  booting. (`| union()` was rejected: it works, but reorders the line, which makes diffs useless
  and reads like corruption.)
- **Never edits `vfio-pci.conf`.** If the GPU is bound there *by ID*, the role **refuses and stops**
  rather than "fixing" the line — the other ids on it are passed through to running VMs, and an
  ACS override cannot help a device bound by id anyway.
- **Backs up before writing**, reads the file back, and asserts the on-disk content matches the
  intent before touching the bootloader.
- **Never reboots.** It reports that a reboot is required and prints the rollback command.
- **Idempotent.** Applying twice is a no-op, and the second run does not overwrite the backup or
  re-run `proxmox-boot-tool`.

## Rollback

GRUB hosts:

```bash
ls /etc/default/grub.bak-*
cp /etc/default/grub.bak-<stamp> /etc/default/grub
update-grub && reboot
```

systemd-boot hosts:

```bash
ls /etc/kernel/cmdline.bak-*
cp /etc/kernel/cmdline.bak-<stamp> /etc/kernel/cmdline
proxmox-boot-tool refresh && reboot
```

The role prints this with the real timestamp after applying. Because the change is a single kernel
cmdline token, rollback is genuinely a one-liner.

## What it deliberately does NOT do

- **Reboot.** A hypervisor reboot takes down every guest on it, so it stays an operator decision;
  check readiness first and confirm the driver binding afterwards.
- **Touch any VM's `hostpci` config.** Other guests' passthrough is out of scope.
- **Edit `vfio-pci.conf`** — see above.
- **Edit a GRUB line that is not a simple double-quoted assignment.** A trailing comment or single
  quotes cause a refusal, because appending to those shapes can silently place the token inside a
  shell comment where it never reaches the kernel — and the read-back gate cannot detect that,
  since it re-reads with the same extraction.
- **Proceed when no driver can claim the card.** If nothing on the running kernel has a PCI alias
  for the device, the role refuses: freeing it would bind nothing, and the result would look like
  the ACS override having failed. Override with `gpu_passthrough_require_driver=false` to stage the
  change ahead of a kernel upgrade.
- **Guarantee the group actually splits.** Whether an ACS override separates a given topology is a
  property of the hardware, discoverable only by rebooting. A post-reboot check is what answers
  it, and the rollback path is what makes finding out cheap.

## Test coverage (honest)

`molecule/default/` runs the **real role** against a fake `lspci` and a fixture cmdline (more than the
"parse/check only" tier usual for Proxmox roles). Genuinely covered: the append-if-missing logic, token-order preservation, both
hard gates, the backup/read-back path, idempotence, and all four refusal paths (GPU bound by id,
GPU absent, malformed GRUB line, no capable driver on the running kernel). Both bootloader paths
are covered.

**Not covered, and not claimed:** `update-grub`/`proxmox-boot-tool refresh` (both stubbed — they
need a real bootloader), apt installation, and whether the ACS override splits a real IOMMU group.
The last is hardware behaviour, learnable only by rebooting the host.
