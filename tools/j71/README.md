# Pinned J71 research preparation

These tools preserve this fork's A1474/J71 preparation work. They are separate
from the Omarchy A release builder and do not establish working J71 support.
See [the recorded results](../../docs/j71-bringup.md). Installation work is on
hold; none of the preparation commands below boots or flashes a device.

Use Python 3.11+, Git and [uv](https://docs.astral.sh/uv/getting-started/installation/)
on Linux or macOS. Keep the Orchard checkout and build staging on a native,
case-sensitive filesystem. Windows checkout line-ending and mode conversion can
change component source keys; these scripts use LF, and the Orchard clone disables
automatic CRLF conversion. `pins.json` is the reviewed source/component selection.

## Prepare a RAM image

From this repository:

```sh
bash tools/j71/setup
```

The default Orchard checkout is `~/projects/OrchardLinux/orchard-j71`. Set
`J71_ORCHARD` to use an existing checkout at the pinned commit. An existing
different checkout is refused, never reset. The command fetches matching
published components, stages the RAM project under ignored `.work/j71/ram`,
builds through that checkout's launcher, and verifies the result. It accesses
no iPad. `--output DIRECTORY` chooses a different RAM project directory.

With a pinned Orchard checkout already prepared, the equivalent is:

```sh
/path/to/orchard/bin/orchard python tools/j71/prepare.py --output .work/j71/ram
```

The Pongo download has an explicit size bound and pinned SHA256. Orchard checks
the other published components against its source keys and release checksums.
Missing/mismatching published components cause a failure instead of a local
kernel or loader build. Generated host keys and receipts stay local.

## Compare public restore metadata

```sh
/path/to/orchard/bin/orchard python tools/j71/fetch_reference.py
python3 tools/j71/compare_reference.py --input .work/j71/reference
```

The first command reads only the necessary ranges from Apple's public restore
image and verifies the manifest/device-tree digests. The second compares
selected resource properties. Outputs, including Apple's bytes, remain in
ignored `.work/`. These inputs cannot replace the unit's running ADT/calibration.

## Build a portable native Linux kit

This optional kit targets **Linux x86-64 hosts**, carries the existing compiled
components, and generates the host's own RAM SSH identity during preparation.
It contains no user firmware, calibration, private keys or raw device logs.
Internet may be needed for uv's Python dependencies on first use.

```sh
/path/to/orchard/bin/orchard python tools/j71/build_native_kit.py \
  --stage ~/projects/OrchardLinux/j71-kit-stage \
  --archive out/j71-native-kit.tar.gz
python3 tools/j71/verify_native_kit.py out/j71-native-kit.tar.gz
```

Use a new staging directory on a native Linux filesystem and a new archive
path outside that directory. Existing outputs are refused. `--uv PATH` can
select the Linux x86-64 uv executable to bundle. The builder assembles and
verifies a fresh RAM image without accessing a device; the archive excludes
that test image, virtualenvs, private validation state and Git reflogs.
`verify_native_kit.py` performs a fresh safe extraction and checks its hashes,
source revision, shell syntax and exclusions.

The kit's README describes the future manual hardware test. `run.sh` checks the
exact J71 DFU identity and unchanged image before Orchard's interactive boot
prompt; its one attempt is bounded to 180 seconds. Run it only after the owner's
go and readiness. No helper retries a boot automatically. Do not use the
upstream distribution installer on A1474 as though installation were qualified.

## Fork hygiene

- Keep upstream kernel, firmware recipes, drivers and board data in Orchard.
- Retain upstream licensing/attribution; these helpers are GPL-2.0-or-later.
- Commit source, pins and sanitized outcomes, not generated images or unit data.
- The one-off Windows driver/reset scripts and local session files are retained
  privately under `.work/`; they are not a portable or supported Windows boot path.
- Do not add a changelog entry without the explicit approval required by AGENTS.md.
