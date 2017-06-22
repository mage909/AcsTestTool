#!/bin/bash
# Usage: ./stability_warmboot.sh deviceID
if [ $# -lt 1 ];then
    echo "please input the device ID,the script exit."
    exit 1
fi
device=$1
#LOOP_WB=10000
LOG=warmboot_${device}.log
cat /dev/null > $LOG
echo "The device id is $device" >> $LOG
i=1
#while [ $i -le $LOOP_WB ]
while true
do
	# echo "WarmBoot LOOP $i started at BEHCH time: `date` ### DUT time:`adb -s $device shell date`" >> $LOG
	adb -s $device reboot
	adb -s $device wait-for-device
    timer=1
#    until [[ `adb -s ${device} shell getprop sys.boot_completed` =~ "1" || $timer == 60 ]]
    until [[ `adb -s ${device} shell getprop sys.boot_completed` =~ "1" ]]
    do
        sleep 3
        let timer=timer+1
    done
	# echo "WarmBoot LOOP $i ended at BEHCH time: `date` ### DUT time: `adb -s $device shell date`"  >> $LOG
    if [ $timer -eq 60 ];then
#		adb -s $device reboot
        echo ">>>Wait for loop $i boot_completed timeout<<<" | tee -a $LOG
#exit 1
    fi
#	adb -s $device shell getprop | grep boot >> $LOG
	echo "------> DUT $device: warmboot loop $i" | tee -a $LOG
	let i=i+1
done
