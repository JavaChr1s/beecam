#!/bin/bash
if grep -q "maxcpus=1 " /boot/cmdline.txt
then
    mount -o remount,rw /boot
    sed -i 's/maxcpus=1 /maxcpus=4 /g' /boot/cmdline.txt
    mount -o remount,ro /boot
    reboot
else
    echo "Performance-Mode is already enabled"
fi