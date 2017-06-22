#!/bin/bash
device=$1
LOOP_WB=$2
LOG=bt_onoff_${device}.log
cat /dev/null > $LOG
echo "The device id is $device" >> $LOG

adb -s $device shell input keyevent 3
sleep 3
adb -s $device wait-for-device root
adb -s $device shell service call bluetooth_manager 6 > /dev/null 2>&1
sleep 5
i=1
while [ $i -le $LOOP_WB ]
# while true
do
    adb -s $device shell service call bluetooth_manager 6 > /dev/null 2>&1
    sleep 5
    # BT off
    adb -s $device shell service call bluetooth_manager 8 > /dev/null 2>&1
    echo "------> DUT $device: BT on/off loop $i" | tee -a $LOG
    sleep 5
    let i=i+1
done
