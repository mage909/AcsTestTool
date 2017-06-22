#!/bin/bash
date=`date "+%Y-%m-%d"`
devices=`adb devices|grep -w device|awk {'print $1'}`

mkdir -p $1
cd $1

mv ../../../Stress_Case/*.log .
mv ../../../Stress_Case/*.result .
mv ../../../Stress_Case/Monkey/*.log .
mv ../../../Stress_Case/Monkey/*.txt .

for device in $devices;
do
{
	if [ `timeout 5 adb -s $device shell getprop ro.serialno` ]
	then
		mkdir $device
		cd $device

		timeout 10 adb -s $device wait-for-device root
		timeout 10 adb -s $device wait-for-device
		sleep 3

		adb -s $device pull /sys/fs/pstore pstore
		if [[ -d pstore ]] && [ `ls pstore | wc -l` -eq 0 ]
		then
    	    rm -rf pstore
		fi

		adb -s $device shell "rm -rf /data/logs/events"
		adb -s $device pull /data/logs data_logs
		adb -s $device pull /mnt/sdcard/logs data_logs
    	adb -s $device pull /storage/sdcard1/Coredump Coredump

		if [[ -d Coredump ]] && [ `ls Coredump | wc -l` -eq 0 ]
		then
		    rm -rf Coredump
		fi
		cd ..
	fi
}&
done
wait
cd ../..
