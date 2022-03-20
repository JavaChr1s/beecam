#!/bin/bash
function updateGit() {
	git fetch -v
	git reset --hard origin/master
}

updateGit
