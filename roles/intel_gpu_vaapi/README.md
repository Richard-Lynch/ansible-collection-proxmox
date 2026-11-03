# intel_gpu_vaapi

Installs the VA-API userspace an Intel GPU needs on a Debian bookworm host (such
as a Proxmox VE 8 node), and proves it works by opening that GPU's own render
node with `vainfo`.

An Intel Arc (Battlemage) card can be bound by the `xe` driver while `vainfo`
still fails with `va_openDriver() returns -1`, because bookworm's libva has no
`xe` backend. The newer libva and media driver come from `bookworm-backports`.

## What it does

1. Reads the current state, without changing anything: running kernel, the GPU's
   PCI address (found from `vaapi_device_id`), its bound driver, its own
   `renderD*` node (found through the PCI device in sysfs, not by listing
   `/dev/dri`), and the installed libva, media driver and `vainfo`.
2. Fails if the GPU is absent, has no host driver (for example it is still bound
   to `vfio-pci`), or has no render node.
3. Runs `vainfo` on that render node. If VA-API already works, it reports so and
   stops.
4. With `vaapi_apply: false` (the default) it reports what it would install and
   stops.
5. With `vaapi_apply: true` it:
   - adds the backports suite as its own `sources.list.d` file;
   - pins that suite at priority 100 for every package, so nothing comes from it
     unless asked;
   - installs `vaapi_packages` from the backports suite by name (never a
     dist-upgrade);
   - re-reads the installed versions, runs `vainfo` again, and fails unless
     VA-API now works;
   - reports whether HEVC Main10, AV1 and H.264 profiles are available.

Probing a fixed `/dev/dri/renderD128` would test whichever device enumerates
first, so on a host with a working iGPU it could pass while the discrete card is
broken. That is why the role resolves the render node from the GPU's PCI
address.

## Inputs

| Option                     | Type | Required | Default                                                            | Description                                                                                     |
| -------------------------- | ---- | -------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `vaapi_device_id`          | str  | yes      |                                                                    | PCI `vendor:device` of the GPU, for example `8086:e20c`                                         |
| `vaapi_apply`              | bool | no       | `false`                                                            | `false` probes and reports; `true` enables the pinned backports suite and installs the packages |
| `vaapi_packages`           | list | no       | `intel-media-va-driver-non-free`, `libva2`, `libva-drm2`, `vainfo` | Packages installed from the backports suite                                                     |
| `vaapi_backports_suite`    | str  | no       | `bookworm-backports`                                               | Suite that provides the newer VA-API stack                                                      |
| `vaapi_stable_suite`       | str  | no       | `bookworm`                                                         | Stable suite, named in the rollback instructions                                                |
| `vaapi_sysfs_base`         | str  | no       | `/sys/bus/pci/devices`                                             | Where PCI devices are enumerated; set only by the molecule scenario to point at a fixture tree  |
| `vaapi_backports_filename` | str  | no       | `ansible-vaapi-backports`                                          | Basename of the `sources.list.d` and `preferences.d` files this role writes                     |

## Usage

```yaml
- hosts: gpu_hosts
  become: true
  roles:
    - role: richard_lynch.proxmox.intel_gpu_vaapi
      vaapi_device_id: "8086:e20c"
      vaapi_apply: "{{ vaapi_apply_flag | default(false) }}"
```

## Rollback

Both files the role writes share the `vaapi_backports_filename` basename:
`/etc/apt/sources.list.d/<basename>.list` and
`/etc/apt/preferences.d/<basename>`. To roll back, downgrade the packages to the
stable suite (`apt-get install --allow-downgrades <pkg>/<vaapi_stable_suite>`)
and remove both files.

## Testing

`molecule/default/` runs the real role offline against a fixture sysfs tree and
fake `lspci`, `vainfo` and `dpkg-query`. The apt transaction and the pin are not
exercised.
