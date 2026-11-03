# proxmox_vzdump

Reconcile a **cluster-wide nightly `vzdump` backup job** (all guests) via `pvesh` — the local copy
in a 3-2-1 backup model (cheap, per-guest full backups; complements storage-level snapshots and an
offsite copy).

## What it does

Runs on **one** PVE node (the job is written to cluster-shared `/etc/pve/jobs.cfg`, so it applies
fleet-wide). Via `pvesh .../cluster/backup`:

1. Asserts the target storage has `content=backup`.
2. Finds our job by a **stable comment tag** (`ansible-managed-nightly`).
3. **Creates** it if absent, **updates** it only if a tracked field drifted (idempotent — `pvesh set`
   can't report change, so the role compares first).

Retention via PVE `prune-backups` (keep-daily/weekly/monthly). Mode `snapshot` for consistent-ish live
backups. Compression `zstd`.

## Inputs

See [`meta/argument_specs.yml`](meta/argument_specs.yml). Key ones:
- `proxmox_vzdump_storage` — backup-capable storage (default `local-backups`, the Directory storage
  `proxmox_storage_layout` creates). Point at an NFS/PBS storage for an offsite copy.
- `proxmox_vzdump_schedule` — default `02:45` (off the hour and half-hour, where snapshot schedules
  commonly run).
- `proxmox_vzdump_all` / `proxmox_vzdump_exclude` — all guests, minus excluded VMIDs (e.g. CI staging).
- `proxmox_vzdump_keep_*` — retention.
- `proxmox_vzdump_enabled` — create enabled (default true).

## Usage

```yaml
- hosts: pve1             # any one node: the job lives in cluster-shared /etc/pve/jobs.cfg
  become: true
  roles:
    - role: richard_lynch.proxmox.proxmox_vzdump
```

Any single online node applies it cluster-wide.

## Notes

- Excludes the ephemeral CI staging VMIDs by default is NOT set — add them to
  `proxmox_vzdump_exclude` if you don't want short-lived staging guests backed up.
- `local` (`/var/lib/vz`) is on each node's system disk; for real durability use a dedicated volume
  (`proxmox_storage_layout`) or an NFS/PBS store.

## Testing

`molecule/default/` exercises the reconcile logic offline (no live cluster): matches our job by comment
tag (not a stranger's), takes the create path when absent, and updates only when a field drifted.
