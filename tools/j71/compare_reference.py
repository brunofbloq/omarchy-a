# SPDX-License-Identifier: GPL-2.0-or-later
"""Compare public J71/J72 ADT resources, without assigning untested hardware support."""
import json
import argparse
from pathlib import Path
import re
import struct

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True, help="directory produced by fetch_reference.py")
args = parser.parse_args()
root = args.input.expanduser().resolve()

def nodes(blob):
    position = 0
    found = {}

    def read_node(parent, depth=0):
        nonlocal position
        if depth > 64 or position + 8 > len(blob):
            raise ValueError("Node bounds")
        count, children = struct.unpack_from("<II", blob, position)
        position += 8
        if count > 4096 or children > 4096:
            raise ValueError("Node count")
        props = {}
        for _ in range(count):
            if position + 36 > len(blob):
                raise ValueError("Property header bounds")
            name = blob[position:position + 32].split(b"\0", 1)[0].decode("ascii")
            size = struct.unpack_from("<I", blob, position + 32)[0] & 0xffffff
            position += 36
            padded = (size + 3) & ~3
            if position + padded > len(blob):
                raise ValueError("Property bounds")
            props[name] = blob[position:position + size]
            position += padded
        name = props["name"].split(b"\0", 1)[0].decode("ascii")
        path = parent + "/" + name
        found[path] = props
        for _ in range(children):
            read_node(path, depth + 1)

    read_node("")
    if position != len(blob):
        raise ValueError("Trailing ADT bytes")
    return found

j71 = nodes((root / "j71ap.adt").read_bytes())
j72 = nodes((root / "j72ap.adt").read_bytes())
rows = []
for path in sorted(set(j71) | set(j72)):
    if not re.search(r"spi|touch|wlan|wifi|hdq|ans|pmgr|pmu|gpio|i2c", path, re.I):
        continue
    a, b = j71.get(path), j72.get(path)
    differences = sorted(k for k in set(a or {}) | set(b or {})
                         if (a or {}).get(k) != (b or {}).get(k))
    rows.append({"path": path, "j71_present": a is not None, "j72_present": b is not None,
                 "different_properties": differences,
                 "j71": {k: v.hex() for k, v in (a or {}).items()},
                 "j72": {k: v.hex() for k, v in (b or {}).items()}})
report = {"public_restore_metadata_only": True, "ios": "12.5.8", "build": "16H88",
          "hardware_qualified": False, "nodes": rows}
(root / "resource-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"nodes_j71": len(j71), "nodes_j72": len(j72), "resources_compared": len(rows),
                  "differing_resources": [{"path": row["path"], "properties": row["different_properties"]}
                                          for row in rows if row["different_properties"]]}, indent=2))
