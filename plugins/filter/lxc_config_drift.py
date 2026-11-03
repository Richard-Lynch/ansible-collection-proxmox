# SPDX-License-Identifier: GPL-3.0-or-later
"""Decide whether a running LXC's configuration differs from the declared one.

Used by the deployment_proxmox_lxc role as richard_lynch.proxmox.dpl_lxc_*. A collection filter rather than the
role's own filter_plugins/ because a role inside a collection never loads its own plugin
directories. One file exposes four filters, so each has a sidecar .yml with its documentation.

WHY THIS EXISTS. `community.general.proxmox` with `update: true` decides for itself whether
anything changed, and its comparison is wrong for two keys every caller sets, so it reports
"has been updated" and re-PUTs the config on EVERY run:

* `tags` arrives as a LIST and PVE returns a `;`-joined STRING, compared with
  `str(['ansible', 'docker']) != 'ansible;docker'` -> always different.
* `description` comes back from PVE with a trailing newline (each `#` comment line of the config
  file is one line of the description), so `"LXC web"` never equals `"LXC web\\n"`.

A role that then RESTARTS any running guest reboots it on every converge. The re-PUT also
rewrites the file, which fights `proxmox_lxc_docker_fix`: PVE parses EVERY `#` line of a
container config into the description, so blockinfile `# BEGIN/END` markers become description
text, the PUT replaces the description and drops them, and a marker-based fix re-inserts its
block (with a second copy of its `lxc.*` lines) and reboots again — one duplicate pair per
converge.

So the role asks THIS function, with the live config read from the API, and calls the update
only when it returns something. Keys the caller did not declare are not compared: PVE adds its
own (`hwaddr`, `type=veth`, `digest`, an `mp0` owned by another play) and they are not drift.

THE MAC. "Live extras are not drift" is right for the COMPARISON and wrong for the WRITE: the
module replaces each `netN` value wholesale, so an update that re-PUTs net0 without the `hwaddr`
PVE generated makes PVE generate a NEW one, and the guest takes a new DHCP lease — a
description-only drift would move the guest's address and break anything holding the old one.
So `lxc_update_netif` decides what the update writes for the interfaces: nothing at all unless
an interface itself drifted, and when one did, every interface carries its LIVE hwaddr.
"""

import json
import re

# Keys whose change PVE applies to a running container without a restart, or which are pure
# metadata. Drift in ONLY these does not justify rebooting the guest.
NO_RESTART_KEYS = frozenset({"description", "tags", "onboot", "startup"})


def _items(value):
    """`k=v,k=v` -> {'k': 'v'}; a bare token (e.g. a volume id) maps to itself."""
    out = {}
    for part in str(value).split(","):
        part = part.strip()
        if not part:
            continue
        key, sep, val = part.partition("=")
        out[key] = val if sep else key
    return out


def _subset_drift(current, desired):
    """Every declared k=v must be present in the live value; live extras are not drift."""
    if current is None:
        return True
    live = {k: _bool_text(v) for k, v in _items(current).items()}
    return any(live.get(k) != _bool_text(v) for k, v in _items(desired).items())


def _bool_text(value):
    """PVE stores a boolean as 1/0; a declared `firewall: true` renders as `True`."""
    return {"true": "1", "false": "0"}.get(str(value).lower(), str(value))


def _norm_text(value):
    lines = [line.rstrip() for line in str(value or "").split("\n")]
    return "\n".join(lines).strip()


def _tags(value):
    if value is None:
        return set()
    if isinstance(value, (list, tuple)):
        return {str(t).strip() for t in value if str(t).strip()}
    return {t for t in re.split(r"[;, ]+", str(value)) if t}


def _int(value, default=None):
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in ("true", "yes", "on"):
        return 1
    if text in ("false", "no", "off"):
        return 0
    return int(float(text))


def lxc_config_drift(current, desired):
    """Return {key: {'current': ..., 'desired': ...}} for every declared key that differs.

    `current` is the dict PVE's `GET /nodes/{node}/lxc/{vmid}/config` returns. `desired` holds,
    in the shapes the role declares them:
      hostname, description (str); cores, memory, swap (int); onboot (bool);
      tags (list); features, startup (dict); net (dict netN -> 'k=v,...' or a JSON string);
      rootfs ({'storage': str, 'size_gb': int}).
    A desired key whose value is None is not compared.
    """
    current = current or {}
    drift = {}

    def record(key, cur, want):
        drift[key] = {"current": cur, "desired": want}

    for key in ("hostname",):
        if desired.get(key) is not None and str(current.get(key)) != str(desired[key]):
            record(key, current.get(key), desired[key])

    if desired.get("description") is not None:
        if _norm_text(current.get("description")) != _norm_text(desired["description"]):
            record("description", current.get("description"), desired["description"])

    for key in ("cores", "memory", "swap"):
        if desired.get(key) is not None and _int(current.get(key)) != _int(desired[key]):
            record(key, current.get(key), desired[key])

    if desired.get("onboot") is not None:
        # PVE omits `onboot` when it is off, so absent means 0.
        if _int(current.get("onboot"), 0) != _int(desired["onboot"]):
            record("onboot", current.get("onboot"), desired["onboot"])

    if desired.get("tags") is not None and _tags(current.get("tags")) != _tags(desired["tags"]):
        record("tags", current.get("tags"), desired["tags"])

    for key in ("features", "startup"):
        want = desired.get(key)
        if not want:
            continue
        want_str = ",".join("%s=%s" % (k, v) for k, v in want.items())
        if _subset_drift(current.get(key), want_str):
            record(key, current.get(key), want_str)

    net = desired.get("net") or {}
    if isinstance(net, str):
        net = json.loads(net)
    for key, want in net.items():
        if _subset_drift(current.get(key), want):
            record(key, current.get(key), want)

    rootfs = desired.get("rootfs")
    if rootfs:
        live = str(current.get("rootfs") or "")
        storage_ok = live.split(":", 1)[0] == str(rootfs["storage"])
        size_ok = _items(live).get("size") == "%sG" % _int(rootfs["size_gb"])
        if not (storage_ok and size_ok):
            record("rootfs", live or None, "%s:%s" % (rootfs["storage"], rootfs["size_gb"]))

    return drift


def _net(value):
    if isinstance(value, str):
        return json.loads(value) if value.strip() else {}
    return dict(value or {})


def lxc_netif_with_live_hwaddr(net, current):
    """Every declared netN, with the live interface's hwaddr appended unless one is declared.

    A declared `hwaddr=` wins: that is configuration, not something to second-guess. An interface
    that does not exist yet (or a live one with no hwaddr) is returned unchanged, so PVE assigns one.
    """
    current = current or {}
    out = {}
    for key, want in _net(net).items():
        want = str(want)
        live_mac = _items(current.get(key) or "").get("hwaddr")
        if live_mac and "hwaddr" not in _items(want):
            want = "%s,hwaddr=%s" % (want, live_mac)
        out[key] = want
    return out


def lxc_update_netif(net, current, drift):
    """The `netif` an update should send: {} (omit it) unless a declared interface drifted.

    When one did, ALL declared interfaces are sent, each with its live hwaddr — a netN value is
    replaced wholesale by PVE, and one without hwaddr gets a freshly generated MAC.
    """
    net = _net(net)
    if not set(drift or {}) & set(net):
        return {}
    return lxc_netif_with_live_hwaddr(net, current)


def lxc_drift_needs_restart(drift):
    """True when any drifted key is one a running container only picks up on restart."""
    return bool(set(drift or {}) - NO_RESTART_KEYS)


class FilterModule(object):
    def filters(self):
        return {
            "dpl_lxc_config_drift": lxc_config_drift,
            "dpl_lxc_drift_needs_restart": lxc_drift_needs_restart,
            "dpl_lxc_netif_with_live_hwaddr": lxc_netif_with_live_hwaddr,
            "dpl_lxc_update_netif": lxc_update_netif,
        }
