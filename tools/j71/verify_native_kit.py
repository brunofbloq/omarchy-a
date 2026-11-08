# SPDX-License-Identifier: GPL-2.0-or-later
"""Verify the actual archive after a fresh safe extraction; no device access."""
from pathlib import Path
import json
import subprocess
import sys
import tarfile
import tempfile

if len(sys.argv) != 2:
    raise SystemExit("Usage: verify_native_kit.py ARCHIVE.tar.gz")
archive = Path(sys.argv[1]).expanduser().resolve()
with tempfile.TemporaryDirectory(prefix="j71-kit-unpack-") as temporary:
    with tarfile.open(archive) as tar:
        tar.extractall(temporary, filter="data")
    root = Path(temporary) / "j71-native-kit"
    subprocess.run(["sha256sum", "--quiet", "-c", "SHA256SUMS"], cwd=root, check=True)
    assert not (root / "source/.venv").exists()
    assert not (root / "project/out").exists()
    assert not (root / "source/.git/logs").exists()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root / "source", text=True).strip()
    expected = json.loads((root / "pins.json").read_text(encoding="utf-8"))
    assert commit == expected["orchard"]["commit"]
    for script in ("prepare.sh", "run.sh", "install-usb-rules.sh"):
        subprocess.run(["sh", "-n", str(root / script)], check=True)
print("PASS: fresh safe extraction, all input hashes, source revision, shell syntax and runtime/private-data exclusions")
