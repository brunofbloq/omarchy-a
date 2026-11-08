#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-or-later
set -eu
group=$(id -gn)
case "$group" in ''|*[!a-zA-Z0-9_-]*) echo 'Unsupported group name' >&2; exit 1 ;; esac
temporary=$(mktemp)
trap 'rm -f "$temporary"' EXIT HUP INT TERM
for pid in 1227 4141 4144; do
    printf 'SUBSYSTEM=="usb", ATTR{idVendor}=="05ac", ATTR{idProduct}=="%s", MODE="0660", GROUP="%s"\n' "$pid" "$group" >> "$temporary"
done
printf 'SUBSYSTEM=="tty", ATTRS{idVendor}=="05ac", ATTRS{idProduct}=="4144", MODE="0660", GROUP="%s"\n' "$group" >> "$temporary"
target=/etc/udev/rules.d/71-omarchy-j71.rules
if [ -e "$target" ] && ! cmp -s "$temporary" "$target"; then
    echo "An existing $target differs; review it manually. Nothing overwritten." >&2
    exit 1
fi
sudo install -m 644 "$temporary" "$target"
sudo udevadm control --reload-rules
