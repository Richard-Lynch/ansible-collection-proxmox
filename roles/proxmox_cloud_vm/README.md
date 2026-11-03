# proxmox_cloud_vm

Create or converge **one** cloud-init VM on the Proxmox node the play runs on, from a checksummed
cloud image. It serves workloads that need a real kernel rather than a container (for example a
sysbox runtime), where `deployment_proxmox_vm` does not fit: it sets no VLAN tag, clones from a
template that must exist on the node, and restarts a RUNNING VM on every converge
(`tasks/clone.yml`'s ternary).

## What it does, in order

1. Gates (`tasks/_gates.yml`): balloon floor not above the ceiling; image is an https URL in a dated
   release directory (never `current`/`latest`/`daily`) with a full sha256; the key is a public key
   line; the image directory is a plain absolute path.
2. Reads the cluster's guests and **refuses** a vmid that belongs to another guest, another node or
   a container. An unreadable guest list is not "the vmid is free"; the role refuses.
3. Downloads the image (once, verified against the pinned sha256) and creates the VM with
   `qm create` (every value its own argv element, no shell) only when the vmid is absent.
4. On an existing VM, converges `memory`, `balloon`, `cores`, `onboot`, `startup`, `tags` and
   `description`, one `qm set` per differing key, and **only grows** the disk.
5. Starts a stopped VM. A running VM is never restarted. Memory and cores changed on a running VM
   are "pending" in Proxmox until it is rebooted; that reboot is the operator's decision.
   **Guest agent:** the Ubuntu cloud image ships WITHOUT `qemu-guest-agent`, so the VM is created with
   `--cicustom vendor=<snippet storage>:snippets/vm-<vmid>-vendor.yaml` (written by the role; installs
   and starts the agent). Without it the VM boots and the agent wait times out. cloud-init runs vendor-data for a NEW instance only, so an existing VM without it is
   refused with a message to rebuild it, not waited on.
6. Reads the configuration back (NIC on the declared bridge and VLAN tag, guest agent enabled, disk
   at least the declared size, cores and memory) and waits for `qm agent <vmid> ping`. The wait is
   `until:` with the module's own failure, so a VM that never boots fails the task.

## Inputs

All site configuration (node, vmid, VLAN, sizes, key) comes from inventory through the calling
play; see `meta/argument_specs.py` (the generated `argument_specs.yml` and `defaults/main.yml` are
not hand-edited). Required: `proxmox_cloud_vm_node`, `_vmid`, `_name`, `_cores`, `_memory_mb`,
`_disk_gb`, `_vlan_tag`, `_ssh_public_key`, `_image`.

## What is deliberately not here

* **Cloud-init changes after create** (user, key, address). They apply when the VM is created;
  changing them is a rebuild decision, not a converge. The role does not compare `sshkeys` (Proxmox
  stores it URL-encoded, and a comparison that is always unequal would make every run `changed`).
* **Moving a NIC to another VLAN.** The read-back asserts the VLAN and fails if an existing VM
  differs; it does not rewrite a live VM's network.
* **A DHCP reservation.** The VM takes a lease; reserve its address in your DHCP server first if it
  must not move.

## Tests

`molecule test` is render-only (the role acts on a node, which CI is not): it proves each gate
passes a good input and each refuses a bad one **naming itself**, and that the create command and the
desired-settings dictionary say what they must (VLAN on the NIC, imported verified image, agent on,
key as a file argument, no password, `--startup` only when an order is declared). The on-node
read-backs in `tasks/main.yml` prove the VM itself when the role runs on a node.
