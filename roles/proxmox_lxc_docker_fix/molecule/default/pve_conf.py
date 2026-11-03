# SPDX-License-Identifier: GPL-3.0-or-later
"""A minimal model of how PVE reads and writes /etc/pve/lxc/<vmid>.conf.

Used by this scenario to stand in for the Proxmox API on both sides of a converge:
`parse` is what `GET .../config` returns, `put` is a `PUT .../config` followed by PVE's rewrite of
the file. It models only the behaviour the two roles' fixed point depends on, after PVE::LXC::Config's
parse_pct_config / write_pct_config:

* EVERY `#` line in the main section is one line of `description`, wherever it sits.
* `lxc.*` lines are kept, in order and duplicates included, as raw pairs; the API cannot set them
  and a PUT never touches them.
* A rewrite emits the description first (one `#` line each), then the keys sorted, then the raw
  lxc.* pairs, then any `[section]`, verbatim.

The model reproduces what a marker-based fix leaves behind when it loops: a `description` holding
both blockinfile markers and an `lxc` list holding one identical pair per converge.

  pve_conf.py parse <file>              -> JSON of the API view
  pve_conf.py put <file> '<json dict>'  -> apply the keys and rewrite the file
"""

import json
import sys
from urllib.parse import unquote


def parse(text):
    conf, lxc, descr, sections = {}, [], [], []
    in_main = True
    for line in text.split("\n"):
        if line.startswith("["):
            in_main = False
        if not in_main:
            sections.append(line)
            continue
        if not line.strip():
            continue
        if line.startswith("#"):
            descr.append(unquote(line[1:]))  # PVE::Tools::decode_text
            continue
        key, _sep, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if key.startswith("lxc."):
            lxc.append([key, value])
        else:
            conf[key] = value
    if descr:
        conf["description"] = "\n".join(descr) + "\n"
    if lxc:
        conf["lxc"] = lxc
    return conf, sections


def write(conf, sections):
    out = ["#" + line for line in conf.get("description", "").split("\n") if line != ""]
    for key in sorted(conf):
        if key in ("description", "lxc", "digest"):
            continue
        out.append("%s: %s" % (key, conf[key]))
    out += ["%s: %s" % (k, v) for k, v in conf.get("lxc", [])]
    body = "\n".join(out) + "\n"
    if sections:
        body += "\n" + "\n".join(sections).rstrip("\n") + "\n"
    return body


def main():
    action, path = sys.argv[1], sys.argv[2]
    with open(path) as fh:
        conf, sections = parse(fh.read())
    if action == "parse":
        print(json.dumps(conf))
        return
    if action == "put":
        for key, value in json.loads(sys.argv[3]).items():
            conf[key] = ";".join(value) if key == "tags" else str(value)
        with open(path, "w") as fh:
            fh.write(write(conf, sections))
        return
    sys.exit("unknown action %r" % action)


if __name__ == "__main__":
    main()
