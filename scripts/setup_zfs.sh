#!/bin/bash
# ZFS Setup Script for LuciferOS

echo "[+] Installing ZFS on Linux..."
apt install -y zfsutils-linux

echo "[+] Creating encrypted ZFS pool..."
# Note: Requires raw device (e.g., /dev/sdb)
# For USB: zpool create -f lucifera /dev/sdb
# For VM: zpool create -f lucifera /dev/vda

# Create encrypted root dataset
zfs create -o encryption=aes-256-gcm -o keylocation=prompt lucifera/root

# Enable compression
zfs set compression=lz4 lucifera/root

# Create separate datasets
zfs create lucifera/root/tools
zfs create lucifera/root/payloads
zfs create lucifera/root/cache
zfs create lucifera/root/logs

# Mount all
zfs mount -a

echo "[+] ZFS encrypted filesystem ready"
