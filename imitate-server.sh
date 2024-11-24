#!/usr/bin/bash

workdir="$(pwd)"
curdate="$(date)"
ret=$(echo -e "${workdir}\t${curdate}")
file=~/imitate-server.log

# write to file
echo "${ret}" >> "${file}"
# output to screen
echo -e "Starting server @ ${workdir}...\n${curdate}"

# Stay open
sleep 1h
