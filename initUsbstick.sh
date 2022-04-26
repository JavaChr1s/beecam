#!/bin/bash
function initUsbstick() {
	echo "Init usbstick start"
	waitForMount
	mountAsRW

	createFolderIfNotExists "/media/usbstick/analyzed"
	createFolderIfNotExists "/media/usbstick/data"
	createFolderIfNotExists "/media/usbstick/error"
	createFolderIfNotExists "/media/usbstick/raw"
	initMotionEye
	echo "Init usbstick done"
}

function waitForMount() {
	echo "-------------------------------"
	echo "Waiting for mount"

	count=0
	count_max=600

	mount|grep usbstick > /dev/null 2>&1
	while [ $? -ne 0 ]; do
	echo -e "\e[1A\e[K $(date): test mounted [$count/$count_max] - /media/usbstick"
	sleep 1
	let "count+=1"
	[[ ${count} -gt ${count_max} ]] && exit 1
	mount|grep usbstick > /dev/null 2>&1
	done

	echo "$(date): Mounted - /media/usbstick"
}

function mountAsRW() {
	echo "-------------------------------"
	echo "Waiting for mount as RW"

	count=0
	count_max=600

	echo raspberry | sudo -S mount -o rw,remount /media/usbstick/
	grep "[[:space:]]rw[[:space:],]" /proc/mounts | grep usbstick > /dev/null 2>&1
	while [ $? -ne 0 ]; do
	echo -e "\e[1A\e[K $(date): test mount as rw [$count/$count_max] - /media/usbstick"
	sleep 1
	let "count+=1"
	[[ ${count} -gt ${count_max} ]] && exit 1
	grep "[[:space:]]rw[[:space:],]" /proc/mounts | grep usbstick > /dev/null 2>&1
	done

	echo "$(date): Mounted as rw - /media/usbstick"
}

function createFolderIfNotExists() {
	local folder=$1
	echo "-------------------------------"
	echo "checking folder $folder"
	if [ -d "${folder}" ] ; then
		echo "$folder is a directory"
	else
		echo "$folder is not a directory, removing file if exists and create a directory!"
		rm -f $folder
		mkdir -p $folder
	fi
}

function initMotionEye() {
	createFolderIfNotExists "/media/usbstick/motioneye"
	# override configs if exists
	cp /home/pi/repo/motioneye/motioneye/camera-1.conf /media/usbstick/motioneye/ -fv
	cp /home/pi/repo/motioneye/motioneye/motion.conf /media/usbstick/motioneye/ -fv
	cp /home/pi/repo/motioneye/motioneye/motioneye.conf /media/usbstick/motioneye/ -fv
	cp /home/pi/repo/motioneye/motioneye/tasks.pickle /media/usbstick/motioneye/ -fv
	# don't override mask if exists
	cp /home/pi/repo/motioneye/motioneye/mask_1.pgm /media/usbstick/motioneye/ -nv
}

initUsbstick
