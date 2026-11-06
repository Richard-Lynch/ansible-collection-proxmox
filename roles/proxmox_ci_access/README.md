# proxmox_ci_access

Creates a **least-privilege PVE identity for a CI pipeline** (user, role, ACL and a privsep API
token), so a self-hosted runner never touches Proxmox as `root@pam`.

## What it creates (idempotently, via `pveum` on a PVE node)

- User **`proxmox_ci_access_user`** (e.g. `ci-staging@pve`)
- Role **`proxmox_ci_access_role`** (e.g. `CIStaging`) — guest ops + host read only:
  `VM.Allocate/Audit/Config.*/PowerMgmt`, `Datastore.Allocate*/Audit`, `Sys.Audit`, `SDN.Use`.
  **Deliberately excludes** `Sys.Modify`, `Realm.*`, `User.Modify`, `Permissions.Modify` → the CI
  user **cannot reconfigure the host, mint tokens, or self-escalate**.
- ACL granting the role to the user (and to the token, since privsep tokens carry their own privs)
  on `proxmox_ci_access_acl_path` (default `/`; narrow it to a pool to confine CI to its guests)
- API token **`<user>!<proxmox_ci_access_token>`** (privsep)

## Inputs

See [`meta/argument_specs.yml`](meta/argument_specs.yml). The user, role and token names are
required: they are the caller's to choose.

## Usage

```yaml
- hosts: pve1              # any PVE node (example name) — /etc/pve is cluster-shared
  roles:
    - role: richard_lynch.proxmox.proxmox_ci_access
      vars:
        proxmox_ci_access_user: ci-staging@pve
        proxmox_ci_access_role: CIStaging
        proxmox_ci_access_token: staging
        proxmox_ci_access_secret_name: <your secret store item>   # named in the creation message
        proxmox_ci_access_secret_dest: /path/on/the/controller/ci-token   # written 0600 on creation
```

On **first** creation the role writes the token secret **once** to `proxmox_ci_access_secret_dest`
on the controller (mode 0600) and prints only that path. Store the secret in your secret manager
immediately and delete the file; it cannot be retrieved from Proxmox later. The secret is never
printed, because a task's output is recorded by whatever records the run. A run that would create
the token without `proxmox_ci_access_secret_dest` set stops before creating it.

## Rotation

Re-runs are no-ops. To rotate the token: `pveum user token remove <user> <token>` then re-run this
role (it recreates the token and writes the new secret to `proxmox_ci_access_secret_dest`). This makes the credential regeneratable from the role alone.

## Testing

`molecule/default/` runs in check/parse mode (a real PVE API isn't in CI): it asserts the role's
tasks parse and the priv list excludes the dangerous privileges.
