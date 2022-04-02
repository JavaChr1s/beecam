#!/bin/bash
docker stop $(docker ps -a -q)
echo raspberry | sudo -S poweroff