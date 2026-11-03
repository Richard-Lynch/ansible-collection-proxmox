# vm_truenas

Creates a TrueNAS VM on a Proxmox VE node from an installer ISO, then pauses for
the parts of the install that are done by hand.

## What it does

1. Looks the VM up by `truenas_vm_id`. If it already exists, the role does
   nothing else.
2. Otherwise:
   1. downloads the ISO to the node's local ISO directory with
      `proxmox_iso_download`;
   2. creates the VM through the API (`community.general.proxmox_kvm`,
      `state: present`): q35 machine, OVMF firmware with a 4m EFI disk and no
      pre-enrolled keys, the guest agent enabled, start on boot, tags `ansible`
      and `truenas`;
   3. attaches the ISO as a CD-ROM on `ide2`, a boot disk `scsi0` of
      `truenas_vm_disk_size` GB on `truenas_vm_storage` (excluded from backups,
      no cache, discard, iothread), the PCI devices in `truenas_vm_hostpci`, and
      one virtio NIC on `truenas_vm_bridge` tagged with `truenas_vm_vlan.id`;
   4. starts the VM;
   5. **pauses** until the operator has run the installer from the Proxmox
      console;
   6. detaches the ISO, sets the boot order to `scsi0` and restarts the VM
      (`tasks/cleanup_boot.yml`);
   7. **pauses** again for the remaining manual setup in the TrueNAS web UI.

Because of the two pauses, the role needs an interactive run.

`truenas_password` and `truenas_callback_url` are required by the argument spec,
but no task reads them.

The API calls authenticate with `proxmox.user` and `proxmox.password`.

## Entrypoints

| Entrypoint     | Does                                             |
| -------------- | ------------------------------------------------ |
| `main`         | Everything above                                 |
| `cleanup_boot` | Only step 2.6: detach the ISO and restart the VM |

## Inputs

| Option                     | Type | Required | Default     | Description                                              |
| -------------------------- | ---- | -------- | ----------- | -------------------------------------------------------- |
| `proxmox`                  | dict | yes      |             | `api_host`, `user`, `password`, `node`                   |
| `truenas_vm_iso_url`       | str  | yes      |             | URL of the TrueNAS installer ISO                         |
| `truenas_vm_id`            | int  | yes      |             | VMID                                                     |
| `truenas_vm_name`          | str  | yes      |             | VM name                                                  |
| `truenas_vm_startup_order` | int  | yes      |             | Proxmox start order                                      |
| `truenas_vm_bridge`        | str  | yes      |             | Bridge for the NIC                                       |
| `truenas_vm_vlan`          | dict | yes      |             | VLAN of the NIC; the role reads `id`                     |
| `truenas_vm_hostpci`       | dict | no       |             | `hostpci0`..`hostpci9`, each a `proxmox_kvm` `hostpci` string such as `host=0000:01:00.0,pcie=1` |
| `truenas_vm_storage`       | str  | no       | `local-lvm` | Storage for the boot disk and EFI disk                   |
| `truenas_vm_disk_size`     | int  | no       | `64`        | Boot disk size in GB                                     |
| `truenas_vm_memory`        | int  | no       | `16384`     | Memory in MiB                                            |
| `truenas_vm_cores`         | int  | no       | `4`         | vCPU cores                                               |
| `truenas_password`         | str  | yes      |             | Declared, not used                                       |
| `truenas_callback_url`     | str  | yes      |             | Declared, not used                                       |

## Usage

Run on the Proxmox VE node that will hold the VM:

```yaml
- hosts: pve_nodes
  become: true
  roles:
    - role: richard_lynch.proxmox.vm_truenas
      proxmox: "{{ proxmox_api }}"
      truenas_vm_iso_url: https://example.com/TrueNAS-SCALE.iso
      truenas_vm_id: 600
      truenas_vm_name: nas
      truenas_vm_startup_order: 1
      truenas_vm_bridge: vmbr0
      truenas_vm_vlan: { id: 60 }
      truenas_vm_hostpci:
        hostpci0: "host=0000:01:00.0,pcie=1"
      truenas_password: "{{ truenas_admin_password }}"
      truenas_callback_url: https://nas.example.com
```

## Requirements

`community.general.proxmox_kvm` and `proxmox_vm_info`, and their `proxmoxer`
Python dependency.
