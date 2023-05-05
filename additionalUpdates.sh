#!/bin/bash

# PERFORMANCE

# Disable ethernet
ifconfig eth0 down 

# THIS DOES ACTUALLY NOT WORK BECAUSE OF OTHER DRIVER
# disable HDMI output
#/opt/vc/bin/tvservice -o
# enable HDMI output
#/opt/vc/bin/tvservice -p