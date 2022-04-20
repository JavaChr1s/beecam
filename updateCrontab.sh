#!/bin/bash

function updateCrontab() {
	rw
	usedCrontab=`sed '/#BEECAM-START/,/#BEECAM-END/!d;//d' /etc/crontab | tr -d '\n' | sed -E "s/,\s*/\n/g"`
	currentCrontab=$(cat crontab.txt | sed -e 's/\//\\\//g')
	if [ "$currentCrontab" != "$usedCrontab" ]; then
		echo "Updating crontab!"
		perl -i -pe "BEGIN{undef $/;} s/#BEECAM-START.*#BEECAM-END/#BEECAM-START\n$currentCrontab\n#BEECAM-END/smg" /etc/crontab
		/etc/init.d/cron reload
	fi
	ro
}

updateCrontab
