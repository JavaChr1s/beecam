#!/bin/bash

function updateCrontab() {
	usedCrontab=`sed '/#BEECAM-START/,/#BEECAM-END/!d;//d' /etc/crontab | tr -d '\n' | sed -E "s/,\s*/\n/g"`
	file="/home/pi/repo/crontab.txt"
	if [ -f "/media/usbstick/config/crontab.txt" ]; then
		echo "Using crontab file from usbstick!"
		file="/media/usbstick/config/crontab.txt"
	fi
	currentCrontab=$(cat $file | sed -e 's/\//\\\//g')
	if [ "$currentCrontab" != "$usedCrontab" ]; then
		echo "Updating crontab!"
		perl -i -pe "BEGIN{undef $/;} s/#BEECAM-START.*#BEECAM-END/#BEECAM-START\n$currentCrontab\n#BEECAM-END/smg" /etc/crontab
		/etc/init.d/cron reload
	fi
}

updateCrontab
