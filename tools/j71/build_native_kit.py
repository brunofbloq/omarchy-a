# SPDX-License-Identifier: GPL-2.0-or-later
"""Package and validate native-host preparation; never boot or query the iPad."""
import hashlib
import argparse
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

from common import HERE, components, pins

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--stage", type=Path, required=True, help="new directory on a native Linux filesystem")
parser.add_argument("--archive", type=Path, required=True, help="new output .tar.gz outside the staging directory")
parser.add_argument("--uv", type=Path, default=shutil.which("uv"), help="Linux x86-64 uv executable")
args = parser.parse_args()
if sys.platform != "linux" or platform.machine() not in ("x86_64", "amd64"):
    raise SystemExit("This portable kit targets native Linux x86-64 hosts")
kit = args.stage.expanduser().resolve()
archive = args.archive.expanduser().resolve()
if archive.is_relative_to(kit):
    raise SystemExit("The output archive must be outside its staging directory")
if kit.exists() or archive.exists():
    raise SystemExit("A native kit already exists; inspect it instead of overwriting it.")
if args.uv is None or not args.uv.is_file():
    raise SystemExit("Supply a Linux x86-64 uv binary with --uv")
inputs = components()
from orchard import published
ROOT, kernel, loader, tools = (inputs[name] for name in ("root", "kernel", "loader", "tools"))
selected = pins()
commit, tag = (selected["orchard"][name] for name in ("commit", "release"))
kit.mkdir(parents=True)
archive.parent.mkdir(parents=True, exist_ok=True)
source = kit / "source"
subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "clone",
                "--no-hardlinks", str(ROOT), str(source)], check=True)
subprocess.run(["git", "-C", str(source), "remote", "set-url", "origin",
                selected["orchard"]["repository"]], check=True)
assert subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() == commit
tool_key = published.shared_keys(ROOT)["tools"]
assert published.shared_keys(source)["tools"] == tool_key
target_tools = kit / "cache/components-v2/tools-published" / tool_key
shutil.copytree(tools, target_tools)
target_kernel = kit / "components/kernel"
target_kernel.mkdir(parents=True)
for name in ("Image.gz", "kernel.release"):
    shutil.copy2(kernel / name, target_kernel / name)
shutil.copytree(kernel / "dtbs", target_kernel / "dtbs")
shutil.copy2(loader, kit / "components/m1n1.bin")
shutil.copy2(inputs["pongo"], kit / "components/pongo.bin")
shutil.copy2(inputs["checkra1n"], kit / "components/checkra1n")
(kit / "host-tools").mkdir()
shutil.copy2(args.uv, kit / "host-tools/uv")
for executable in (kit / "host-tools/uv", kit / "components/checkra1n"):
    executable.chmod(0o755)
(kit / "project").mkdir()
for name in ("init", "orchard.toml"):
    shutil.copyfile(HERE / "payload" / name, kit / "project" / name)
(kit / "project/init").chmod(0o755)
for name in ("prepare.sh", "run.sh", "install-usb-rules.sh", "README.md"):
    shutil.copyfile(HERE / "native" / name, kit / name)
    (kit / name).chmod(0o755 if name.endswith(".sh") else 0o644)
for name in ("preflight.py", "pins.json"):
    shutil.copyfile(HERE / name, kit / name)

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

provenance = {"orchard_commit": commit, "orchard_release": tag,
              "hardware_qualified": False, "architecture": "native Linux x86-64 host; arm64 4 KiB guest",
              "components": {name: digest(kit / "components" / name)
                             for name in ("m1n1.bin", "pongo.bin", "checkra1n")},
              "tools_source_key": tool_key,
              "privacy": "No owner firmware, calibration, logs, ECID or private SSH key packaged."}
(kit / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
# Only immutable inputs belong in SHA256SUMS. Git bookkeeping, cache usage records,
# virtualenvs and runtime outputs are mutable and are checked by their owners.
tracked = subprocess.check_output(["git", "-C", str(source), "ls-files", "-z"]).split(b"\0")
inputs = [source / os.fsdecode(name) for name in tracked if name]
inputs += [p for group in (kit / "components", kit / "host-tools", kit / "project")
           for p in group.rglob("*") if p.is_file()]
inputs += [p for p in target_tools.iterdir() if p.name in published.TOOLS]
inputs += [kit / name for name in ("prepare.sh", "run.sh", "install-usb-rules.sh", "README.md", "provenance.json", "preflight.py", "pins.json")]

def write_sums():
    (kit / "SHA256SUMS").write_text("".join(
        f"{digest(path)}  {path.relative_to(kit).as_posix()}\n" for path in sorted(inputs)))

write_sums()
for name in ("prepare.sh", "run.sh", "install-usb-rules.sh"):
    subprocess.run(["sh", "-n", str(kit / name)], check=True)
with tempfile.TemporaryDirectory(prefix="j71-kit-validation-", dir=kit.parent) as private:
    env = {**os.environ, "ORCHARD_HOME": str(Path(private) / "store")}
    with archive.with_suffix(archive.suffix + ".build.log").open("w") as log:
        subprocess.run(["sh", str(kit / "prepare.sh")], env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    verify_code = "from orchard.ram import verify_ram; import sys; r=verify_ram(sys.argv[1]); assert 'j71' in r['boards']; print(r['kernel_release'])"
    release = subprocess.check_output([str(source / ".venv/bin/python"), "-c", verify_code,
                                       str(kit / "project/out/apple-4k")], env=env, text=True).strip()
    assert release == "7.3.0-rc1-orchard-apple-4k"
    subprocess.run(["git", "-C", str(source), "diff", "--exit-code"], check=True, stdout=subprocess.DEVNULL)
validation = {"shell_syntax": "PASS", "new_host_ram_build": "PASS", "orchard_verify_ram": "PASS",
              "kernel_release": release, "device_accessed": False, "hardware_boot": "NOT RUN"}
(kit / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
inputs.append(kit / "validation.json")
write_sums()

def portable(member):
    relative = Path(member.name).relative_to("j71-native-kit")
    parts = relative.parts
    if (".venv" in parts or "__pycache__" in parts or any(p.endswith(".egg-info") for p in parts)
            or parts[:2] == ("project", "out")
            or parts[:3] == ("source", ".git", "logs")
            or parts[:3] in (("source", ".git", "FETCH_HEAD"), ("source", ".git", "ORIG_HEAD"))):
        return None
    member.uid = member.gid = 0
    member.uname = member.gname = ""
    return member

with tarfile.open(archive, "w:gz") as tar:
    tar.add(kit, arcname="j71-native-kit", filter=portable)
with tarfile.open(archive) as tar:
    names = tar.getnames()
    assert not any("/private/" in name or name.endswith("/id_ed25519") for name in names)
    assert "j71-native-kit/validation.json" in names
(archive.with_suffix(archive.suffix + ".sha256")).write_text(f"{digest(archive)}  {archive.name}\n")
print(json.dumps({"archive": str(archive), "bytes": archive.stat().st_size,
                  "sha256": digest(archive), "validation": validation}, indent=2))
