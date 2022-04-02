#!/bin/bash
function recreateService() {
	local folder=$1
	echo "Going to recreate container within $folder"
	cd $folder
	docker-compose -f $COMPOSE_FILE_NAME down
	docker-compose -f $COMPOSE_FILE_NAME up -d
	cd ..
}

recreateService "motioneye"
recreateService "object_detection"
recreateService "webhook"