#!/bin/bash
function updateGit() {
	git fetch
	git reset --hard origin/master
}

updateGit
