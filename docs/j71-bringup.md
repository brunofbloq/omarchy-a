# iPad Air Wi-Fi J71 research status

Recorded 8 November 2026. Device installation work is on hold. This fork preserves
the preparation and findings so future work can resume from reviewed inputs.

## Scope and identity

| Field | Target |
| --- | --- |
| Case model | A1474 |
| Product | iPad4,1 |
| Board | J71AP / `j71` |
| SoC / DFU CPID | Apple A7 / `0x8960` |
| DFU BDID | `0x10` |
| Observed iOS | 12.5.8 / 16H88 |
| Kernel platform | `apple-4k`, AArch64 with 4 KiB pages |

J71b (iPad 6), J72 (iPad Air Cellular, BDID `0x12`) and J72b are separate
targets. The J72 project is a useful implementation reference, not a J71 image.
Hardware data, kernels, device trees, firmware conversion and boot transports
remain owned by Orchard. This fork adds research preparation alongside the
distribution; its release builder and hardware capability declarations are not
modified to claim J71 installation support.

## Evidence

| Gate | Result | What this establishes |
| --- | --- | --- |
| Exact DFU identity | Passed | The connected target matched CPID `0x8960`, BDID `0x10`. |
| Published component selection | Passed | Kernel, m1n1 and tools matched the pinned Orchard source keys; downloaded assets were hash checked. |
| RAM image assembly | Passed | `verify_ram` accepted the assembled image and its J71 DTB. |
| Native Linux kit preparation | Passed without a device | A fresh image assembled from the portable checkout; archive extraction, source revision and input hashes passed. |
| WSL boot attempt 1 | Failed before Pongo | checkm8 asynchronous-transfer failure and USB reset/descriptor timeouts. |
| WSL boot attempt 2 | Failed before Pongo | Initial checkm8 setup succeeded; the trigger stage timed out after USB disconnected. One requested cable reconnect was performed. |
| Return to iOS | Observed | The owner confirmed the iOS lock screen; normal iOS USB was subsequently observed. |
| Linux, USB serial/SSH and desktop | Not reached | No feature qualification follows from an assembled image or exploit setup. |
| Storage installation | Not attempted | No partition resize, filesystem installation or storage write was performed. |

The test host was Windows x86-64 with Ubuntu WSL2 and usbipd-win 5.3.0. Normal
USB enumeration also intermittently reported a device-descriptor failure.
A targeted Windows PnP restart temporarily restored normal enumeration. The
failure therefore does not isolate one definitive cause; it does show that
this WSL setup is not a qualified J71 boot path. Temporary USB sharing bindings
were removed and the bootstrap processes stopped after testing.

The next distinct hardware experiment would use native Linux or macOS with
direct USB. It has **not** been run. A native Windows alternative was inspected:
the reviewed openra1n stage-2 switch lacks an A7 (`0x8960`) payload despite
recognizing the identity. gaster's Windows pwned-DFU support alone does not
provide a complete A7-to-Pongo bootstrap.

## Public restore-tree comparison

The J71 and J72 device trees from Apple's iOS 12.5.8 / 16H88 restore image were
read using HTTP byte ranges. The BuildManifest and J71 DeviceTree matched
Orchard's SHA256 pins; both device trees matched the verified manifest digests.
This downloaded 137,214 range bytes in the recorded run, not the entire IPSW.

The comparison covered 21 selected resource nodes out of 116 J71 and 121 J72
nodes. Some touchscreen rail-function byte strings differ only in their first
phandle word. Resolve those references before interpreting this as common
wiring. The Wi-Fi `module-instance` differs materially:

| Board | Public restore metadata |
| --- | --- |
| J71 Wi-Fi | `syrah` |
| J72 Cellular | `dureza` |

These are public restore trees, not the owner's running ADT or panel
calibration. No driver, GPIO, regulator, charging grant or firmware/NVRAM
configuration was copied on the basis of this comparison.

## Reproduction and future gates

[The preparation workflow](../tools/j71/README.md) pins Orchard to
`897686d9415634000eb202fe1d492e6bdb9d9d64`
(`nightly-20261106-897686d94156`). It builds RAM artifacts only and refuses
implicit local compilation when matching published components are unavailable.
The payload mounts virtual/RAM filesystems, disables module autoloading, and
calls Orchard's normal ACM/NCM/SSH helper. It does not mount internal storage.

Future hardware work requires a new owner go for every boot, one attempt at a
time, bounded device commands, private logs and a verified return to iOS.
Require a new Linux boot ID, the expected kernel, working USB serial and SSH,
and dmesg before advancing to touch, networking, battery or the desktop.
Installation is a later, separately reviewed operation after J71 storage and
recovery support are qualified; never copy the J72 partition layout or charging
policy. Keep firmware, unit calibration, device IDs, credentials, raw logs and
generated images outside public commits.

The session's local files remain under ignored `.work/`; they are not source
artifacts for this fork. The curated changelog was not edited.

## Sources

- [Pinned J72 reference inventory and adaptation boundaries](j72-reference.md)
- [Orchard device rules](https://github.com/OrchardLinux/orchard/blob/897686d9415634000eb202fe1d492e6bdb9d9d64/AGENTS.md)
- [Orchard J71 descriptor](https://github.com/OrchardLinux/orchard/blob/897686d9415634000eb202fe1d492e6bdb9d9d64/devices/j71/device.toml)
- [J72 replication guide](https://github.com/thisiscamk/ipad-air-j72-linux/blob/1addefe99cc3793c068594cfcb4ecf5497e0cb34/QUICKSTART.md)
- [J72 project](https://github.com/thisiscamk/ipad-air-j72-linux)
- [Reviewed openra1n source](https://github.com/mineek/openra1n/blob/4595a5333e4134ade77b43fb2259e880b85801ee/openra1n.c)
- [Windows gaster fork](https://github.com/vvaske/gaster-win-mac)
