# proxmox_template_lxc

Downloads an LXC container template to a Proxmox VE storage through the API, and
checks that the storage lists it.

## Entrypoints

| Entrypoint | Does                                                                                                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `main`     | Downloads the template (`community.general.proxmox_template`, `content_type: vztmpl`, `state: present`), then runs `pvesm list <storage> --content vztmpl` and fails unless the template appears in it |
| `cleanup`  | Removes the template (`state: absent`)                                                                                                                                                                 |

The `pvesm list` check runs on the play's target host, so `main` must target a
Proxmox VE node.

## Inputs

| Option                         | Entrypoints | Type | Required | Default | Description                                                                                                                                                          |
| ------------------------------ | ----------- | ---- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `proxmox`                      | both        | dict | yes      |         | API connection: `api_host`, `user`, `api_token_id`, `api_token_secret`, `node` (plus `cluster`, `password`, `is_primary`, which the spec requires but no task reads) |
| `proxmox_template_lxc_name`    | both        | str  | yes      |         | Template name, for example `debian-12-standard_12.7-1_amd64.tar.zst`                                                                                                 |
| `proxmox_template_lxc_storage` | `main`      | str  | no       | `local` | Storage that receives the template                                                                                                                                   |
| `public_ssh_key`               | `main`      | str  | yes      |         | Required by the argument spec; no task reads it                                                                                                                      |

## Usage

```yaml
- hosts: pve_nodes
  become: true
  roles:
    - role: richard_lynch.proxmox.proxmox_template_lxc
      proxmox: "{{ proxmox_api }}"
      public_ssh_key: "{{ ssh_public_key }}"
      proxmox_template_lxc_name: debian-12-standard_12.7-1_amd64.tar.zst
```

To remove the template, call it with `tasks_from: cleanup` through
`ansible.builtin.include_role`.

## Requirements

`community.general.proxmox_template` and its `proxmoxer` Python dependency.
