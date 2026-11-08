#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-or-later
# Build the existing RAM experiment on this host; never accesses the iPad.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
cd "$here"
sha256sum --quiet -c SHA256SUMS
export PATH="$here/host-tools:$PATH"
export UV_PYTHON=python3
export ORCHARD_CACHE_DIR="$here/cache"
export ORCHARD_CHECKRA1N="$here/components/checkra1n"
tools_key=$(python3 -c 'import json; print(json.load(open("pins.json"))["tools_key"])')
exec "$here/source/bin/orchard" build "$here/project" --device j71 \
    --kernel-dir "$here/components/kernel" --loader "$here/components/m1n1.bin" \
    --pongo "$here/components/pongo.bin" --busybox "$here/cache/components-v2/tools-published/$tools_key/busybox"
