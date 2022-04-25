#!/bin/bash
function update() {
	echo "INIT BEECAM"
	echo `date`
	echo "Stopping all containers:"
	sudo -u pi docker stop $(docker ps -a -q)
	echo "Remove all containers:"
	sudo -u pi docker rm $(docker ps -a -q)
	createService "webhook"
	sudo -u pi ./initUsbstick.sh
	createService "motioneye"
	createService "object_detection"
	curl http://localhost/beecam # initialize webinterface

	 # update with version on disk to write to overlayfs
	./updateCrontab.sh
	./additionalUpdates.sh

	echo "UPDATE BEECAM"
	waitForConnection
	sudo systemctl restart systemd-timesyncd.service
	sudo mount -o remount,rw /home/pi/repo
	sudo -u pi ./updateGit.sh
	sudo mount -o remount,ro /home/pi/repo
	sudo -u pi ./updateContainer.sh
	./updateCrontab.sh
	./additionalUpdates.sh
	ifconfig -a
}

function createService() {
	local folder=$1
	echo "Going to create container within $folder"
	cd $folder
	sudo -u pi docker-compose -f docker-compose_raspi.yml up -d
	cd ..
}

function waitForConnection() {
	# ip server
	serverAdr="github.com"
	count=0
	count_max=60

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
update >> update.log

sudo -u pi ./pistatus.sh