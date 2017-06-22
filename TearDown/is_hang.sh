#!/bin/bash
if [ `adb devices | grep -w offline | awk '{print $1}' | head -n 1` ]
then
	adb devices | grep -w offline | awk '{printf("The device %s offline\n",$1)}'
fi
devices=`adb devices|grep -w device|awk {'print $1'}`
for device in $devices;
do
{
	if [ `timeout 5 adb -s $device shell getprop ro.serialno` ]
	then
		:	
	else
		echo "The device $device hang"
	fi
}&
done
wait
