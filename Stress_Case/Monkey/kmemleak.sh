#!/bin/bash
device=$1
echo -n "" > ram_$device.txt
while true
do
	adb -s $device root > /dev/null
	adb -s $device wait-for-device
	sleep 3
	adb -s $device shell "date">> "ram_$device.txt"
	adb -s $device shell "dumpsys meminfo">> "ram_$device.txt"
	adb -s $device shell "cat /proc/meminfo">> "ram_$device.txt"
	echo "------------------------kmemleak-------------------------" >> "ram_$device.txt"
	adb -s $device shell "cat /d/kmemleak">> "ram_$device.txt"
	sleep 300
done
