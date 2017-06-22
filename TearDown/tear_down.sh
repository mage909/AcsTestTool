#!/bin/bash
sleep 3

ps aux | grep monkey | grep -v color | awk '{print $2}' | sudo xargs kill -9
# ps aux | grep coldboot | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep warmboot | grep -v color | awk '{print $2}' | sudo xargs kill -9
# ps aux | grep sleep_wakeup | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep kmsg | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep kmem | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep DownloadTool | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep wifi_on_off | grep -v color | awk '{print $2}' | sudo xargs kill -9
ps aux | grep bt_on_off | grep -v color | awk '{print $2}' | sudo xargs kill -9

devices=`adb devices|grep -w device|awk {'print $1'}`
for device in $devices
do
    # if [ `timeout 5 adb -s $device shell getprop ro.serialno` ] && [[ `adb -s $device shell getprop ro.bootmode` =~ 'normal' ]] && [ `adb -s $device shell ps | grep monkey | awk '{print $2}'` ]
    if [ `timeout 5 adb -s $device shell getprop ro.serialno` ] && [[ `adb -s $device shell getprop ro.bootmode` =~ 'normal' ]]
    then
        timeout 5 adb -s $device root
        timeout 10 adb -s $device wait-for-device
        sleep 3
        timeout 10 adb -s $device shell "pkill monkey"
        # adb -s $device shell "ps | grep monkey | awk '{print $2}' | xargs kill -9"
    fi
done
