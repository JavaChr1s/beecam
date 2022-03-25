#!/bin/bash

function removeDeprecatedFstab() {
	perl -i -pe "BEGIN{undef $/;} s/#BEECAM-START.*#BEECAM-END/#BEECAM-START\n\n\n#BEECAM-END/smg" /etc/fstab
}

function installUsbmount() {
	sudo apt-get install usbmount -y
	sudo cp usbmount.conf /etc/usbmount/usbmount.conf
	removeDeprecatedFstab
}

installUsbmount
