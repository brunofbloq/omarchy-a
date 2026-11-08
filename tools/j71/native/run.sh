#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-or-later
# One owner-authorized RAM boot, through the pinned checkout's normal launcher.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
cd "$here"
sha256sum --quiet -c SHA256SUMS
export PATH="$here/host-tools:$PATH"
export UV_PYTHON=python3
export ORCHARD_CACHE_DIR="$here/cache"
export ORCHARD_CHECKRA1N="$here/components/checkra1n"
export ORCHARD_VIA=checkra1n
export PYTHONUNBUFFERED=1
"$here/source/bin/orchard" python "$here/preflight.py" --project "$here/project"
# --yes is intentionally omitted: the operator confirms this attempt in the CLI.
exec timeout -k 5 180 "$here/source/bin/orchard" run "$here/project" --device j71 --no-build
