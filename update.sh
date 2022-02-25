#!/bin/bash
COMPOSE_FILE_NAME="docker-compose_raspi.yml"

function updateAndStart() {
	local container_name=$1
	local folder=$2
	local needUpdate=`checkForUpdate $container_name $folder` # grab the stdout from checkForUpdate
	echo "needUpdate=$needUpdate"
	if [ $needUpdate == "true" ]; then rebuildImage "$folder"; fi
	startService $folder
}

function checkForUpdate() {
	local container_name=$1
	local folder=$2
	local usedVersion=`docker inspect --format '{{ index .Config.Labels "version"}}' $container_name`
	local currentVersion=`grep "LABEL version" "$folder/Dockerfile_raspi" | awk -F= '{print $2}'`
	if [ "$currentVersion" != "$usedVersion" ]; then
		echo "true"
	else
		echo "false"
	fi
}

function rebuildImage() {
	local folder=$1
	cd $folder
	docker-compose -f $COMPOSE_FILE_NAME down --remove-orphans
	docker image prune -af
	docker-compose -f $COMPOSE_FILE_NAME build
	echo "Docker image within $folder was rebuild!"
	cd ..
}

function startService() {
	local folder=$1
	echo "Going to start container within $folder"
	cd $folder
	docker-compose -f $COMPOSE_FILE_NAME up -d
	cd ..
}

function startServer() {
	echo `date`
	git fetch
	git reset --hard origin/master
	updateAndStart "object_detection_analyzer" "object_detection"
	startService "motioneye"
}

function updateCrontab() {
	usedCrontab=`sed '/#BEECAM-START/,/#BEECAM-END/!d;//d' /etc/crontab | tr -d '\n' | sed -E "s/,\s*/\n/g"`
	currentCrontab=$(cat crontab.txt | sed -e 's/\//\\\//g')
	if [ "$currentCrontab" != "$usedCrontab" ]; then
		echo "Updating crontab!"
		perl -i -pe "BEGIN{undef $/;} s/#BEECAM-START.*#BEECAM-END/#BEECAM-START\n$currentCrontab\n#BEECAM-END/smg" /etc/crontab
		/etc/init.d/cron reload
	fi
}

function update() {
	sudo -u pi startServer
	updateCrontab
}

update > /media/usbstick/update.log
