# SPDX-License-Identifier: GPL-2.0-or-later
"""Read verified public restore-image metadata; never communicates with the iPad."""
import hashlib
import argparse
import json
from pathlib import Path
import plistlib
import sys

from common import REPOSITORY, orchard_root

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=REPOSITORY / ".work/j71/reference")
args = parser.parse_args()
from orchard.apple.remote_ipsw import RemoteFile, RemoteZip
from orchard.recipe import im4p_payload
ROOT = orchard_root()
output = args.output.expanduser().resolve()
output.mkdir(parents=True, exist_ok=True)
recipe = json.loads((ROOT / "devices/j71/boot.json").read_text())["firmware"][0]
remote = RemoteFile(recipe["ipsw"]["url"], recipe["ipsw"]["bytes"])
archive = RemoteZip(remote)
manifest_bytes = archive.read("BuildManifest.plist")
if hashlib.sha256(manifest_bytes).hexdigest() != recipe["inputs"]["BuildManifest.plist"]["sha256"]:
    raise SystemExit("BuildManifest checksum differs from Orchard's pin")
manifest = plistlib.loads(manifest_bytes)
rows = []
for board in ("j71ap", "j72ap"):
    identities = [identity for identity in manifest["BuildIdentities"]
                  if identity["Info"]["DeviceClass"] == board]
    if not identities:
        raise SystemExit(f"No {board} identity in the verified BuildManifest")
    entry = identities[0]["Manifest"]["DeviceTree"]
    name = entry["Info"]["Path"]
    blob = archive.read(name)
    digest = entry["Digest"]
    if hashlib.sha1(blob).digest() != digest:
        raise SystemExit(f"{board}: DeviceTree differs from BuildManifest digest")
    if board == "j71ap" and hashlib.sha256(blob).hexdigest() != recipe["inputs"]["DeviceTree"]["sha256"]:
        raise SystemExit("J71 DeviceTree differs from Orchard's SHA256 pin")
    payload = im4p_payload(blob)
    (output / f"{board}.im4p").write_bytes(blob)
    (output / f"{board}.adt").write_bytes(payload)
    rows.append({"board": board, "member": name, "bytes": len(blob),
                 "sha256": hashlib.sha256(blob).hexdigest(),
                 "payload_bytes": len(payload), "header": payload[:8].hex()})
receipt = {"ios": recipe["ipsw"]["version"], "build": recipe["ipsw"]["build"],
           "source": recipe["ipsw"]["url"], "downloaded_bytes": remote.downloaded,
           "devices": rows}
(output / "public-reference.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
