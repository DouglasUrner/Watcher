#!/bin/sh

# Given a URL generate the path name to save it to.

path=$(echo $1 | sed s.^https://..)

echo $path

echo $path | awk '{len = split($0, dirs, "/"); for (i=0; i<len; i++) {print $idirs[i]}}'