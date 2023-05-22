#!/bin/bash

# install maxcpus param
if grep -q "maxcpus=" /boot/cmdline.txt
then
    echo "maxcpus param is already installed"
else
    mount -o remount,rw /boot
    sed -i 's/console=tty1 /console=tty1 maxcpus=4 /g' /boot/cmdline.txt
    mount -o remount,ro /boot
fi

# PERFORMANCE

# Disable ethernet
ifconfig eth0 down 

# THIS DOES ACTUALLY NOT WORK BECAUSE OF OTHER DRIVER
# disable HDMI output
#/opt/vc/bin/tvservice -o
# enable HDMI output
#/opt/vc/bin/tvservice -p