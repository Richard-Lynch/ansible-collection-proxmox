# proxmox_storage_layout

Reconciles a **dedicated PVE backup Directory storage on a thin LV**, so vzdump backups (and ISOs/
templates) live **off the small `root` LV**. Idempotent, online, no reboot.

## Why

The PVE installer default puts `local` (dir storage for backups/ISOs/templates) on the `root` LV, while
`data` (the LVM-thin pool) holds most of the disk but is **block** storage — it can't hold files. On a
single-disk node this fills `root` to 100% while the pool sits mostly idle, and the thin pool **cannot
be shrunk** (lvm2 2.03: *"Thin pool volumes … cannot be reduced in size yet"*) to grow `root`.

The canonical fix (this role): carve a thin LV out of the pool, `mkfs` it, mount it, and register it as
a PVE **Directory** storage for backups. That reclaims the pool's idle space for backups without
touching guest disks or rebooting.

## What it does (idempotent)

1. `lvcreate -V <size> -T <vg>/<thinpool> -n <lv>` — a thin backup volume (skip if present).
2. `mkfs.<fstype>` — **only if the LV has no filesystem** (never reformats a populated volume).
3. mount at `<mount>` + persist in fstab (`nofail`).
4. `pvesm add dir <id>` with `content=backup,iso,vztmpl` + a prune policy (skip if present).
5. verify the storage is active.

Then point `proxmox_vzdump` at the new storage (`proxmox_vzdump_storage: local-backups`).

## Usage

```yaml
- hosts: proxmox          # every node: the LV and mount are per-node, the storage.cfg write runs once
  become: true
  roles:
    - role: richard_lynch.proxmox.proxmox_storage_layout
      vars:
        # REQUIRED: every node that has (or will have) the backup LV, so the storage is valid for a
        # cluster-wide vzdump job
        proxmox_storage_layout_backup_nodes: [pve1, pve2, pve3]
        proxmox_storage_layout_backup_size: 200G
      # defaults: thin LV `vzbackup` → /var/lib/vz-backups → PVE storage `local-backups`
```

## From-scratch procedure (rebuilding a node)

1. Proxmox install (default VG `pve`: `root` + `data` thinpool + `swap`).
2. Run this role → creates the `local-backups` Directory storage from the thin pool.
3. Run `proxmox_vzdump` (targets `local-backups`).
Result: a rebuilt node's backup storage is reproduced by two role runs — no manual `lvcreate` /
`storage.cfg` editing.

## Safety

- Never touches guest disks (`vm-*`, `base-*`) — only creates the named backup LV.
- Won't reformat: `mkfs` runs only when `blkid` finds no filesystem on the LV.
- Thin-provisioned: the backup LV grows as used, capped at its virtual size; keep pool-usage monitored
  and retention bounded (the role sets a storage-level prune policy).

## Testing

`molecule test` runs offline — asserts the task list parses + var defaults are coherent (no live LVM in CI).
