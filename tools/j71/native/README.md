# J71 native Linux RAM test

This is the next boot experiment for iPad Air Wi-Fi A1474 / iPad4,1 / J71AP,
CPID 0x8960, BDID 0x10. **Omarchy is not installed.** No J71 Linux boot has
passed yet. Two Windows/WSL attempts stopped during checkm8, before Pongo.

Use native x86-64 Linux with direct USB, for example Ubuntu's **Try Ubuntu**
session on the same PC. Do not install Ubuntu onto the PC for this test. A VM
or WSL repeats the USB path we are trying to change.

This kit carries the pinned Orchard source, its already compiled 4 KiB kernel
and J71 DTB, matching static tools, m1n1, Pongo 2.6.3, the verified checkra1n
0.1337.3 Linux x86-64 binary, uv and the RAM init. No kernel compilation is
needed. First launch may need internet for uv's small Python dependencies.
Python 3.11+, libusb, OpenSSH, coreutils and udev must be available on the host.
Extract the kit onto a Linux filesystem so executable modes are preserved.

1. With the iPad still in iOS, charge it and keep only this target connected.
2. Run `sh prepare.sh`. It verifies the kit's files and builds a new RAM image
   using this host's SSH key. It does not access the iPad.
3. Run `sh install-usb-rules.sh` to give the current Linux user access to only
   Apple's DFU/Pongo/RAM endpoints. It asks for sudo and refuses to overwrite a
   different existing rule file.
4. Confirm readiness for **one** boot, enter DFU (black screen), then run
   `sh run.sh` in an interactive terminal. Review the identity and confirm the
   CLI prompt. It runs the pinned checkout's `orchard run --no-build`, bounded
   to 180 seconds, without a retry loop. Do not use Restore in Apple software.
5. Require actual Linux evidence: new boot ID, expected kernel
   `7.3.0-rc1-orchard-apple-4k`, USB serial and SSH, and dmesg. Successful loader
   upload is insufficient. The init saves evidence under `/run/j71-evidence/`.
6. Return normally to iOS and verify it before attempting any further feature.

The RAM init mounts only virtual/RAM filesystems, disables module autoloading,
and starts Orchard's ordinary USB ACM/NCM/SSH helper. It does not mount storage,
install a system, resize partitions, or enable charging policy. Keep tests bounded
and use iOS for charging. The USB serial root shell trusts the physically attached
host; use it only with your own computer.

The local preparation/receipt checks in `validation.json` do not qualify USB,
Linux or desktop operation on hardware. Firmware/calibration and storage support
still need J71-specific work after the console gate passes. Public J71 restore
metadata identifies Wi-Fi module `syrah`; do not copy J72's `dureza` settings.

Orchard source pin: `897686d9415634000eb202fe1d492e6bdb9d9d64`, release
`nightly-20261106-897686d94156`. See `provenance.json` and `SHA256SUMS`.
No Apple firmware, unit calibration, raw device logs, ECID or private SSH key is
included. Each host creates its own RAM SSH identity when preparing the image.

Upstream sources and rules:

- https://github.com/OrchardLinux/orchard/blob/897686d9415634000eb202fe1d492e6bdb9d9d64/AGENTS.md
- https://github.com/thisiscamk/ipad-air-j72-linux/blob/main/QUICKSTART.md
