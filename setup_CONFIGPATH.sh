#!/bin/bash
printenv | grep CONFIGPATH
export CONFIGPATH=$(pwd)'/config.yml'
printenv | grep CONFIGPATH

# export CONFIGPATH=/home/urick0s/PycharmProjects/hw-backend-summer-2021-4-course-work/config.yml