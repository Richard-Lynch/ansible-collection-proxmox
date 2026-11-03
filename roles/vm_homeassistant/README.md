# vm_homeassistant

Creates and starts a Home Assistant OS VM on a Proxmox VE node from the
published `.qcow2.xz` image.

## What it does

1. Downloads the image to the node's local ISO directory with
   `proxmox_iso_download`.
2. Decompresses it with `unxz` (skipped when the decompressed file already
   exists).
3. Creates the VM through the API (`community.general.proxmox_kvm`,
   `state: present`): q35 machine, OVMF firmware with a 4m EFI disk and no
   pre-enrolled keys, host CPU type, one socket, the guest agent enabled, start
   on boot, and tags `ansible` and `homeassistant`.
4. Imports the decompressed image as the boot disk `scsi0` on
   `homeassistant_vm_storage` (`import-from=`, `virtio-scsi-single`, iothread,
   discard).
5. Adds one virtio NIC on `homeassistant_vm_bridge`, tagged with
   `homeassistant_vm_vlan.id`, and any USB devices declared in
   `homeassistant_vm_usb`.
6. Starts the VM.

The startup order defaults to the VLAN id when `homeassistant_vm_startup_order`
is not set. `homeassistant_vm_disk_size` is declared but no task reads it: the
disk takes the size of the imported image.

The API calls authenticate with `proxmox.user` and `proxmox.password`, not a
token, because `import-from` a local file path needs a password-authenticated
root login.

## Inputs

| Option                           | Type | Required | Default         | Description                                                                                           |
| -------------------------------- | ---- | -------- | --------------- | ----------------------------------------------------------------------------------------------------- |
| `proxmox`                        | dict | yes      |                 | `api_host`, `user`, `password`, `node`. Not in this role's argument spec, but every API task reads it |
| `homeassistant_vm_iso_url`       | str  | yes      |                 | URL of the `.qcow2.xz` image                                                                          |
| `homeassistant_vm_id`            | int  | yes      |                 | VMID for the new VM                                                                                   |
| `homeassistant_vm_vlan`          | dict | yes      |                 | VLAN of the primary NIC; the role reads `id`                                                          |
| `homeassistant_vm_startup_order` | int  | no       | VLAN id         | Proxmox start order                                                                                   |
| `homeassistant_vm_name`          | str  | no       | `homeassistant` | VM name                                                                                               |
| `homeassistant_vm_bridge`        | str  | no       | `vmbr0`         | Bridge for the NIC                                                                                    |
| `homeassistant_vm_usb`           | dict | no       |                 | `usb0`..`usb9`, each a dict of `proxmox_kvm` `usb` settings, joined as `key=value,...`                |
| `homeassistant_vm_cores`         | int  | no       | `4`             | vCPU cores                                                                                            |
| `homeassistant_vm_memory`        | int  | no       | `8192`          | Memory in MiB                                                                                         |
| `homeassistant_vm_storage`       | str  | no       | `local-lvm`     | Storage for the boot disk and EFI disk                                                                |
| `homeassistant_vm_disk_size`     | str  | no       | `64G`           | Declared, not used                                                                                    |

## Usage

Run on the Proxmox VE node that will hold the VM:

```yaml
- hosts: pve_nodes
  become: true
  roles:
    - role: richard_lynch.proxmox.vm_homeassistant
      proxmox: "{{ proxmox_api }}"
      homeassistant_vm_iso_url: https://example.com/haos_ova-15.2.qcow2.xz
      homeassistant_vm_id: 500
      homeassistant_vm_vlan: { id: 50 }
```

## Requirements

`community.general.proxmox_kvm` and its `proxmoxer` Python dependency, and
`unxz` on the node.
