#!/bin/bash

function updateFstab() {
	uuid=`blkid -s UUID | grep 'sda1' | grep -o -E 'UUID="[a-zA-Z|0-9|\-]*' | cut -c 7-`
	usedUuid=`sed '/#BEECAM-START/,/#BEECAM-END/!d;//d' /etc/fstab | tr -d '\n' | sed -E "s/,\s*/\n/g" | grep -o -E 'UUID=[a-zA-Z|0-9|\-]*' | cut -c 6-`
	echo "usedUUID=$usedUuid"
	echo "currentUUID=$uuid"
	if [ "$currentFstab" != "$usedFstab" ]; then
		echo "Updating /etc/fstab!"
		currentFstab=$(echo "UUID=$uuid /media/usbstick/ vfat utf8,uid=pi,gid=pi,noatime 0" | sed -e 's/\//\\\//g')
		perl -i -pe "BEGIN{undef $/;} s/#BEECAM-START.*#BEECAM-END/#BEECAM-START\n$currentFstab\n#BEECAM-END/smg" /etc/fstab
		reboot
	else
		echo "No /etc/fstab update needed!"
	fi
}

updateFstab
