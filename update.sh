#!/bin/bash
function update() {
	echo `date`
	waitForConnection
	sudo -u pi ./updateGit.sh
	sudo -u pi ./initUsbstick.sh
	sudo -u pi ./updateContainer.sh
	./updateCrontab.sh
	ifconfig -a
}

function waitForConnection() {
	# ip server
	serverAdr="github.com"
	count=0
	count_max=600

	ping -c 1 $serverAdr > /dev/null 2>&1
	while [ $? -ne 0 ]; do
	echo -e "\e[1A\e[K $(date): test connection [$count/$count_max] - ${serverAdr}"
	sleep 1
	let "count+=1"
	[[ ${count} -gt ${count_max} ]] && exit 1
	ping -c 1 $serverAdr > /dev/null 2>&1
	done

	echo "$(date): Connected - ${serverAdr}"
}

cd "$(dirname "$0")"
update >> ../update.log
