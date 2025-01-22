#!/bin/sh

# Given a URL generate the path name to save it to.

path=$(echo $1 | sed s.^https://..)

echo $path