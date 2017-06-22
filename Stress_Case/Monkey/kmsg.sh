#!/bin/bash
device=$1
echo -n "" > kmsg_$device.txt
while true
do
adb -s $device root > /dev/null
adb -s $device wait-for-device
sleep 3
adb -s $device shell "date">> "kmsg_$device.txt"
echo "--------------------------kmsg--------------------------" >> "kmsg_$device.txt"
adb -s $device shell "cat /proc/kmsg">> "kmsg_$device.txt"
sleep 30
done
