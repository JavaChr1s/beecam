#!/bin/bash
function update() {
	echo `date`
	sudo -u pi ./updateGit.sh
	./updateFstab.sh
	sudo -u pi ./updateContainer.sh
	./updateCrontab.sh
}

update > /media/usbstick/update.log
