# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit tests for plugins/filter/lxc_config_drift.py — above all, that an update never changes a MAC.

WHY. An update of a drifted guest that re-PUTs a netN WITHOUT the hwaddr PVE generated makes PVE
generate a NEW MAC (it replaces a netN value wholesale), and the guest takes a new DHCP lease:
a description-only drift would move the guest's address and break anything that resolved the
old one.

Stdlib only. Run from the collection root: python -m pytest tests/unit/test_lxc_config_drift.py
(or run the file directly). deployment_proxmox_lxc's molecule verify runs it too.
"""

import os
import sys
import unittest

# tests/unit/ -> plugins/filter/: two levels up from here, in any collection checkout.
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "plugins", "filter")
)

from lxc_config_drift import (  # noqa: E402
    _items,
    lxc_config_drift,
    lxc_netif_with_live_hwaddr,
    lxc_update_netif,
)

MAC0 = "BC:24:11:00:00:0A"
MAC1 = "BC:24:11:00:00:01"

# A live config as GET /nodes/{node}/lxc/{vmid}/config returns it.
LIVE = {
    "cores": 2,
    "description": "LXC web\n",
    "hostname": "web",
    "memory": 4096,
    "net0": "name=eth0,bridge=vmbr0,gw=192.0.2.1,hwaddr=%s,ip=dhcp,tag=40,type=veth" % MAC0,
    "onboot": 1,
    "rootfs": "local-lvm:vm-101-disk-0,size=32G",
    "swap": 1024,
    "tags": "ansible;docker",
}
# The role's netif as set_vars.yml renders it: no hwaddr, because an inventory rarely declares one.
NET = {"net0": "name=eth0,ip=dhcp,bridge=vmbr0,gw=192.0.2.1,tag=40"}


def desired(**over):
    want = {
        "hostname": "web",
        "description": "LXC web",
        "cores": "2",
        "memory": "4096",
        "swap": "1024",
        "onboot": True,
        "tags": ["ansible", "docker"],
        "net": lxc_netif_with_live_hwaddr(NET, LIVE),
        "rootfs": {"storage": "local-lvm", "size_gb": "32"},
    }
    want.update(over)
    return want


class PreserveMac(unittest.TestCase):
    def test_in_sync_with_live_hwaddr_is_not_drift(self):
        self.assertEqual(lxc_config_drift(LIVE, desired()), {})

    def test_description_only_drift_sends_no_netif(self):
        drift = lxc_config_drift(LIVE, desired(description="other"))
        self.assertEqual(list(drift), ["description"])
        self.assertEqual(lxc_update_netif(NET, LIVE, drift), {})

    def test_vlan_change_keeps_the_hwaddr(self):
        net = {"net0": "name=eth0,ip=dhcp,bridge=vmbr0,gw=192.0.2.1,tag=50"}
        drift = lxc_config_drift(LIVE, desired(net=lxc_netif_with_live_hwaddr(net, LIVE)))
        self.assertEqual(list(drift), ["net0"])
        sent = lxc_update_netif(net, LIVE, drift)
        self.assertEqual(_items(sent["net0"]).get("hwaddr"), MAC0)
        self.assertEqual(_items(sent["net0"]).get("tag"), "50")

    def test_every_interface_carries_its_own_mac_when_one_drifts(self):
        live = dict(
            LIVE,
            net1="name=eth1,bridge=vmbr0,hwaddr=%s,ip=dhcp,tag=20,type=veth" % MAC1,
        )
        net = dict(NET, net1="name=eth1,bridge=vmbr0,ip=dhcp,tag=21")
        drift = lxc_config_drift(live, desired(net=lxc_netif_with_live_hwaddr(net, live)))
        self.assertEqual(list(drift), ["net1"])
        sent = lxc_update_netif(net, live, drift)
        # net0 did not drift but is still sent (the module writes all declared netif keys), so it
        # must carry ITS mac — not net1's, and not none.
        self.assertEqual(_items(sent["net0"]).get("hwaddr"), MAC0)
        self.assertEqual(_items(sent["net1"]).get("hwaddr"), MAC1)

    def test_netif_as_json_string(self):
        # set_vars.yml renders the netif with `tojson`; a string must work the same as a dict.
        drift = {"net0": {}}
        sent = lxc_update_netif('{"net0": "name=eth0,ip=dhcp,tag=50"}', LIVE, drift)
        self.assertEqual(_items(sent["net0"]).get("hwaddr"), MAC0)

    def test_declared_hwaddr_wins(self):
        net = {"net0": "name=eth0,ip=dhcp,hwaddr=AA:AA:AA:AA:AA:AA"}
        out = lxc_netif_with_live_hwaddr(net, LIVE)
        self.assertEqual(out["net0"].count("hwaddr="), 1)
        self.assertEqual(_items(out["net0"]).get("hwaddr"), "AA:AA:AA:AA:AA:AA")

    def test_new_interface_gets_no_invented_mac(self):
        out = lxc_netif_with_live_hwaddr({"net2": "name=eth2,ip=dhcp"}, LIVE)
        self.assertEqual(out, {"net2": "name=eth2,ip=dhcp"})

    def test_absent_container_is_unchanged(self):
        self.assertEqual(lxc_netif_with_live_hwaddr(NET, {}), NET)


if __name__ == "__main__":
    unittest.main(verbosity=2)
