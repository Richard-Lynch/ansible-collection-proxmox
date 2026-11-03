# deployment_proxmox_vm

Clones a Proxmox VE VM from an existing cloud-init template through the Proxmox
API, configures it and starts it, then waits for SSH and installs the QEMU guest
agent inside it.

## What it does

1. Clones `deployment_proxmox_vm_template_name` to a new VM (`vmid`, `name`) on
   `proxmox.node`, on `storage_target` (`community.general.proxmox_kvm`,
   `clone:`).
2. Resizes disk `scsi0` to `size` (`community.general.proxmox_disk`,
   `state: resized`).
3. Updates the VM: `cores`, `memory`, the guest agent flag, `ipconfig0`, the
   cloud-init user and password, the SSH public key and `tags`.
4. Reads the VM's status and starts it, or restarts it if it was already
   running.
5. Waits until SSH answers (`richard_lynch.common.utils_verify_connection`,
   using the VM's `name` as the hostname).
6. Installs and restarts `qemu-guest-agent` on the VM (delegated to the VM by
   `name`).

Only `ipconfig0` is applied to the VM. `ipconfig1` and `ipconfig2` are accepted
by the argument spec but no task reads them.

`tasks/cleanup.yml` and `tasks/undeploy.yml` are placeholders: each one fails on
purpose with `THIS IS NOT CURRENTLY WORKING`. There is no working removal path.

## Inputs

All options are declared in `meta/argument_specs.yml`.

| Option                                | Type | Required | Default | Description                                                                                                                                                                                                                                        |
| ------------------------------------- | ---- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `proxmox`                             | dict | yes      |         | API connection: `api_host`, `user`, `api_token_id`, `api_token_secret`, `node` (plus `cluster`, `password`, `is_primary`, which the spec requires but no task reads)                                                                               |
| `public_ssh_key`                      | str  | yes      |         | Public key written to the VM's cloud-init `sshkeys`                                                                                                                                                                                                |
| `deployment_proxmox_vm_template_name` | str  | yes      |         | Name of the cloud-init VM template to clone                                                                                                                                                                                                        |
| `deployment_proxmox_vm_ci`            | dict | yes      |         | Cloud-init login: `user` and `password` (both required, no default) and `upgrade` (default `true`)                                                                                                                                                 |
| `deployment_proxmox_vm_machine`       | dict | yes      |         | The VM: `name` and `vmid` (required); `cores` (2), `memory` (8192), `size` (`32G`), `storage_target` (`local-lvm` or `local`; default `local-lvm`), `tags` (`[ansible]`), `ipconfig.ipconfig0` (`ip`, `gw`, `ip6`, `gw6`; `ip` defaults to `dhcp`) |

## Usage

```yaml
- hosts: localhost
  gather_facts: false
  roles:
    - role: richard_lynch.proxmox.deployment_proxmox_vm
      proxmox: "{{ proxmox_api }}"
      public_ssh_key:
        "{{ lookup('ansible.builtin.file', '~/.ssh/id_ed25519.pub') }}"
      deployment_proxmox_vm_template_name: debian-12-cloudinit
      deployment_proxmox_vm_ci:
        user: admin
        password: "{{ vm_password }}"
      deployment_proxmox_vm_machine:
        name: app01.example.com
        vmid: 200
        cores: 4
        ipconfig:
          ipconfig0: { ip: 192.0.2.20/24, gw: 192.0.2.1 }
```

## Requirements

- `community.general` (`proxmox_kvm`, `proxmox_disk`, `proxmox_vm_info`) and its
  `proxmoxer` Python dependency on the host that runs the API tasks.
- A cloud-init template that already exists on the target node.
- The VM's `name` must resolve and be reachable over SSH from the controller,
  because the connection check and the guest-agent install connect to it by that
  name.
