#!/bin/sh
temp=`grep -o "t=[0-9]*" /sys/bus/w1/devices/28-3c1b04572da2/w1_slave | sed -e "s/t=//g"`
if [ ${temp} -gt 26000 ]; then
	echo "high"
fi
echo ${temp}
