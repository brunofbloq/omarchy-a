#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read-only guard: require the exact J71 DFU identity and an intact RAM build."""
import argparse
import json
from pathlib import Path


def require_j71(device, target):
    expected = ("dfu", int(target["chip"], 0), int(target["board_id"], 0))
    actual = (device.get("mode"), device.get("chip"), device.get("board"))
    if actual != expected:
        raise ValueError("Expected J71 DFU: CPID 0x8960 / BDID 0x10; refusing boot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    from orchard.apple import usb
    from orchard.ram import verify_ram

    selected = json.loads(Path(__file__).with_name("pins.json").read_text(encoding="utf-8"))
    receipt = verify_ram(args.project.resolve() / "out" / selected["platform"])
    if selected["target"]["board"] not in receipt["boards"]:
        raise ValueError("This payload has no J71 DTB")
    require_j71(usb.sole_target(), selected["target"])
    print("Verified: one J71 DFU device and unchanged RAM payload")


if __name__ == "__main__":
    main()
