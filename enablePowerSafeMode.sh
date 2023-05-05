#!/bin/bash
if grep -q "maxcpus=4 " /boot/cmdline.txt
then
    mount -o remount,rw /boot
    sed -i 's/maxcpus=4 /maxcpus=1 /g' /boot/cmdline.txt
    mount -o remount,ro /boot
    reboot
else
    echo "PowerSafe-Mode is already enabled"
fi