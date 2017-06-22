#!/bin/bash
if [ $# -gt 0 ]
then
    devices=$1
else
    devices=`adb devices|grep -w device|awk {'print $1'}`
fi
for device in $devices;
do
{
    #adb -s $device root
    #adb -s $device wait-for-device
    #sleep 3
    #adb -s $device disable-verity 
    #adb -s $device wait-for-device
    #adb -s $device reboot
    #echo "$device disable-verity done and reboot"
    #adb -s $device wait-for-device
    #until [[ `adb -s ${device} shell getprop sys.boot_completed` =~ "1" ]]
    #do
    #   sleep 2
    #done
    adb -s $device root
    adb -s $device wait-for-device
    sleep 3
    adb -s $device shell "rm -rf mnt/sdcard/logs/*"
    adb -s $device shell "rm -rf /data/logs/aplog*"
    adb -s $device shell "rm -rf /data/logs/crashlog*"
    adb -s $device shell "rm -rf /data/logs/core/*"
    adb -s $device shell "echo -n "" > /data/logs/history_event"
    adb -s $device shell "rm -rf /data/tombstones/*"
    adb -s $device shell "rm -rf /mnt/extSdCard/Coredump/*"
    adb -s $device shell "rm -rf /storage/sdcard1/Coredump/*"
    echo "$device clean logs done"
}&
done
