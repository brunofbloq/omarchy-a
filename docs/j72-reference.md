# J72 reference inventory for future J71 work

Reviewed 8 November 2026. The latest public J72 revision checked was
`1addefe99cc3793c068594cfcb4ecf5497e0cb34`, unchanged from the original review.
This inventory preserves references and provenance. It does not apply patches,
change the J71 component pins, or resume device installation work.

The source repository is
[thisiscamk/ipad-air-j72-linux](https://github.com/thisiscamk/ipad-air-j72-linux/tree/1addefe99cc3793c068594cfcb4ecf5497e0cb34).
Its current-source manifest and Python/publication checks passed locally.
The reference checkout is already present under ignored `.work/` on the
development machine; a fresh clone of this fork does not contain that checkout.

## What to retain and review

| Reference | Why it matters for J71 | Boundary |
| --- | --- | --- |
| [Replication guide](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/QUICKSTART.md) and [source rebuild instructions](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/README.md) | Exact boot sequence, native host assumptions, 4 KiB kernel/module requirements and qualification gates. | The measured host is a Pi 4 running native ARM64 Linux; J71's Windows/WSL attempts did not reach Pongo. |
| [Orchard integration snapshot](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/orchard/0001-j72-orchard-integration-snapshot.patch) | Firmware conversion and recovery/runtime integration to study alongside the A7 hardware changes. | Based on a different Orchard revision from this fork's current preparation pin; includes J72-specific behavior. |
| [Installed-kernel snapshot](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/kernel/0001-j72-installed-kernel-snapshot.patch) and [gauge wait delta](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/kernel/0002-j72-gauge-cache-wait.patch) | A7 SPI/N1 touch, HSIC Wi-Fi, battery and storage implementation references. | Review shared drivers separately from board resources. The snapshot includes experimental storage writes; do not apply it wholesale to J71. |
| [Wi-Fi startup](https://github.com/thisiscamk/ipad-air-j72-linux/tree/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/wifi) | Hardware ordering before NetworkManager and firmware requirements. | J71 restore metadata names `syrah`; J72 names `dureza`. Provision J71's own matching firmware/NVRAM. |
| [Audio implementation and services](https://github.com/thisiscamk/ipad-air-j72-linux/tree/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/audio) | MCA-v1/SmartIO code, overlays and normal PipeWire integration. | Requires private matching firmware. Fresh-boot automation and other audio paths are not fully qualified. |
| [Charging code and tests](https://github.com/thisiscamk/ipad-air-j72-linux/tree/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/charging) | Source admission, supervision, failure handling and reusable test methodology. | The source documents a watchdog failure under browser load. The tested J72 source grant/profile is not a J71 charging authorization. |
| [Progress measurements](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/J72-PROGRESS.md), [validation record](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/VALIDATION.json) and [source manifest](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/code/current/MANIFEST.json) | Distinguish measured functionality, source reconstruction and remaining reliability gaps. | Installed-root success is not a turnkey release or a successful direct bare-loader launch. |

## Exact source bases and patch hashes

The J72 current-source manifest records these bases:

- Orchard: `a6ffc904bf8acb7af2fd0fc94f84ca194bd82ed2`.
- Linux: `4cec5aa77c69ac1fd7c605ab8159714ea9024a08`.
- Tested kernel release: `7.3.0-rc1-j72-pw1-orchard-apple-4k`.

SHA256 of the referenced patches:

| Patch | SHA256 |
| --- | --- |
| Orchard integration snapshot | `11ab025433f2bfbcb40d02b4979e09e1e5485b25ee9b980f2fcbfb56681cf6fc` |
| Installed-kernel snapshot | `98284e8956aa8e8284cb70ecec44ded3e7bbf0967446645def3d8ef05887bc45` |
| Gauge wait delta | `c1ef15281fac9425048d790fc45aa49fd504f62fbb42bdf1b0f0ac4359254e9c` |

Retain the pinned reference repository rather than mixing these snapshots with
its older 7.0.12 experiments. Any later port should reconstruct the stated source
bases, verify/apply patches in a separate Orchard/kernel branch, and preserve
upstream attribution and licenses.

No Apple firmware, another unit's calibration, credentials, partition identifiers
or charging grants should be copied into this fork. Review the J71 resource
comparison and [J71 status](j71-bringup.md) first. When hardware work is explicitly
resumed, the first gate remains a verified J71 RAM console and return to iOS.
