#!/bin/sh
COMMAND="cd /home/pi/repo ; $1 $2 $3 $4"
echo $COMMAND
sshpass -p raspberry ssh -o 'StrictHostKeyChecking no' pi@$(/sbin/ip route|awk '/default/ { print $3 }') $COMMAND 