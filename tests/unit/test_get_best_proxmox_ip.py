# Copyright: (c) 2026, Richard Lynch
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""get_best_proxmox_ip: the address order per guest type, the subnet gate, and the refusals."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "filter"))

from ansible.errors import AnsibleFilterError  # noqa: E402
from get_best_proxmox_ip import FilterModule, get_best_proxmox_ip  # noqa: E402

NET = "192.0.2.0/24"  # TEST-NET-1: the fixture guest network


class LXC(unittest.TestCase):
    def test_lxc_interfaces_win_over_net0(self):
        hv = {
            "proxmox_vmtype": "lxc",
            "proxmox_lxc_interfaces": [{"inet": "192.0.2.5/24"}, {"inet": "192.0.2.6/24"}],
            "proxmox_net0": {"ip": "192.0.2.9/24"},
        }
        self.assertEqual(get_best_proxmox_ip(hv, NET), "192.0.2.5")

    def test_net0_is_the_fallback(self):
        hv = {
            "proxmox_vmtype": "LXC",
            "proxmox_lxc_interfaces": [],
            "proxmox_net0": {"ip": "192.0.2.9/24"},
        }
        self.assertEqual(get_best_proxmox_ip(hv, NET), "192.0.2.9")

    def test_dhcp_and_garbage_are_skipped(self):
        hv = {
            "proxmox_vmtype": "lxc",
            "proxmox_lxc_interfaces": [{"inet": ""}, {"inet": None}],
            "proxmox_net0": {"ip": "dhcp"},
        }
        self.assertIsNone(get_best_proxmox_ip(hv, NET))


class QEMU(unittest.TestCase):
    def test_agent_interfaces_then_ipconfig0(self):
        hv = {
            "proxmox_vmtype": "qemu",
            "proxmox_agent_interfaces": [{"ip-addresses": ["fe80::1", "192.0.2.20"]}],
            "proxmox_ipconfig0": {"ip": "192.0.2.21/24"},
        }
        self.assertEqual(get_best_proxmox_ip(hv, NET), "192.0.2.20")

    def test_ipconfig0_fallback(self):
        hv = {"proxmox_vmtype": "qemu", "proxmox_ipconfig0": {"ip": "192.0.2.21/24"}}
        self.assertEqual(get_best_proxmox_ip(hv, NET), "192.0.2.21")


class Subnet(unittest.TestCase):
    def test_only_the_subnet_qualifies(self):
        hv = {
            "proxmox_vmtype": "lxc",
            "proxmox_lxc_interfaces": [{"inet": "198.51.100.5/24"}, {"inet": "192.0.2.3/24"}],
        }
        self.assertEqual(get_best_proxmox_ip(hv, NET), "192.0.2.3")
        self.assertEqual(get_best_proxmox_ip(hv, subnet="198.51.100.0/24"), "198.51.100.5")
        self.assertIsNone(get_best_proxmox_ip(hv, subnet="203.0.113.0/24"))

    def test_unknown_type_is_none(self):
        self.assertIsNone(
            get_best_proxmox_ip(
                {"proxmox_vmtype": "other", "proxmox_net0": {"ip": "192.0.2.1"}}, NET
            )
        )


class Refusals(unittest.TestCase):
    def test_not_a_dict(self):
        with self.assertRaises(AnsibleFilterError):
            get_best_proxmox_ip("192.0.2.1", NET)

    def test_bad_subnet(self):
        with self.assertRaises(AnsibleFilterError):
            get_best_proxmox_ip({}, subnet="not-a-network")

    def test_registered(self):
        self.assertIn("get_best_proxmox_ip", FilterModule().filters())


if __name__ == "__main__":
    unittest.main()
