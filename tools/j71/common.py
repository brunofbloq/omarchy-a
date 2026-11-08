# SPDX-License-Identifier: GPL-2.0-or-later
"""Pinned research inputs. These helpers are separate from distro release builds."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
MAX_PONGO = 64 * 1024 * 1024


def pins():
    return json.loads((HERE / "pins.json").read_text(encoding="utf-8"))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def orchard_root():
    from orchard.hardware import ROOT
    selected = pins()
    actual = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual != selected["orchard"]["commit"]:
        raise ValueError("Use the Orchard revision in tools/j71/pins.json")
    return ROOT


def components():
    """Use matching published inputs only; never compile or access a device."""
    from orchard import published
    from orchard.cache import shared_cache_root
    from orchard.http import open_url
    from orchard.tools import ensure_tool

    ROOT = orchard_root()
    selected = pins()
    tag = selected["orchard"]["release"]
    cache = shared_cache_root()
    kernel = published.kernel(ROOT, cache, selected["platform"], tag=tag)
    loader = published.m1n1(ROOT, cache, tag=tag)
    tools = published.tools(ROOT, cache, tag=tag)
    if not all((kernel, loader, tools)):
        raise ValueError("Matching published components unavailable; no local compilation attempted")
    if published.shared_keys(ROOT)["tools"] != selected["tools_key"]:
        raise ValueError("Static tool recipe differs from the reviewed pin")
    pongo = cache / "j71-host-inputs" / tag / "pongo.bin"
    if pongo.is_symlink():
        raise ValueError("Refusing a symlinked Pongo cache input")
    if not pongo.exists():
        url = f"https://github.com/OrchardLinux/orchard/releases/download/{tag}/pongo.bin"
        with open_url(url) as response:
            data = response.read(MAX_PONGO + 1)
        if len(data) > MAX_PONGO or hashlib.sha256(data).hexdigest() != selected["pongo_sha256"]:
            raise ValueError("Published Pongo checksum or size mismatch")
        pongo.parent.mkdir(parents=True, exist_ok=True)
        pongo.write_bytes(data)
    if digest(pongo) != selected["pongo_sha256"]:
        raise ValueError("Cached Pongo checksum mismatch")
    return {"root": ROOT, "cache": cache, "kernel": kernel, "loader": loader,
            "tools": tools, "pongo": pongo, "checkra1n": Path(ensure_tool("checkra1n"))}


def stage_payload(project):
    project = Path(project).expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    for name in ("init", "orchard.toml"):
        source, target = HERE / "payload" / name, project / name
        if target.is_symlink():
            raise ValueError(f"Refusing a symlinked payload source: {target}")
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError(f"Refusing to overwrite different payload source: {target}")
        if not target.exists():
            shutil.copyfile(source, target)
    (project / "init").chmod(0o755)
    return project


def build_payload(project, inputs):
    from orchard.ram import verify_ram

    selected = pins()
    project = stage_payload(project)
    subprocess.run([
        str(inputs["root"] / "bin/orchard"), "build", str(project),
        "--device", selected["target"]["board"], "--kernel-dir", str(inputs["kernel"]),
        "--loader", str(inputs["loader"]), "--pongo", str(inputs["pongo"]),
        "--busybox", str(inputs["tools"] / "busybox"),
    ], check=True)
    output = project / "out" / selected["platform"]
    receipt = verify_ram(output)
    if selected["target"]["board"] not in receipt["boards"]:
        raise ValueError("The RAM payload has no J71 DTB")
    if receipt["kernel_release"] != selected["kernel_release"]:
        raise ValueError("Unexpected kernel release")
    return output, receipt
