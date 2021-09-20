#!/bin/bash
printenv | grep CONFIGPATH
export CONFIGPATH=$(pwd)'/config.yml'
printenv | grep CONFIGPATH
