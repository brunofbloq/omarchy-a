#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Prepare and verify the J71 RAM experiment without accessing an iPad."""
import argparse
import json
from pathlib import Path

from common import REPOSITORY, build_payload, components, pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPOSITORY / ".work/j71/ram",
                        help="RAM project directory (default: .work/j71/ram)")
    args = parser.parse_args()
    inputs = components()
    output, receipt = build_payload(args.output, inputs)
    print(json.dumps({"verified": True, "device_accessed": False,
                      "orchard_release": pins()["orchard"]["release"],
                      "output": str(output), "kernel_release": receipt["kernel_release"]}, indent=2))


if __name__ == "__main__":
    main()
