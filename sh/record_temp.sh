#!/bin/sh

target_path="/home/pi/log/"
logfile="temp"`date '+%Y%m%d'`".log"
pastlog="temp"`date '+%Y%m%d' --date '30 day ago'`".log"

if [ -e ${target_path}${pastlog} ]; then
	rm ${target_path}${pastlog}
fi

nowtime=`date '+%Y/%m/%d %H:%M:%S'`
temp=`grep -o "t=[0-9]*" /sys/bus/w1/devices/28-3c1b04572da2/w1_slave | sed -e "s/t=//g"`
if [ -n "$1" ]; then
	temp=$1
fi

echo ${nowtime} ${temp} >> ${target_path}${logfile}
echo $1
