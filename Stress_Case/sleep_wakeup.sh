#!/bin/bash
# Usage: sudo ./sleep_wakeup.sh device_id

#AllOn='\x55\x01\x01\x02\x02\x02\x02\x5F'
#AllOff='\x55\x01\x01\x01\x01\x01\x01\x5B'
#OUT_1_On='\x55\x01\x01\x02\x00\x00\x00\x59'
#OUT_1_Off='\x55\x01\x01\x01\x00\x00\x00\x58'
#OUT_2_On='\x55\x01\x01\x00\x02\x00\x00\x59'
#OUT_2_Off='\x55\x01\x01\x00\x01\x00\x00\x58'
#OUT_3_On='\x55\x01\x01\x00\x00\x02\x00\x59'
#OUT_3_Off='\x55\x01\x01\x00\x00\x01\x00\x58'
#OUT_4_On='\x55\x01\x01\x00\x00\x00\x02\x59'
#OUT_4_Off='\x55\x01\x01\x00\x00\x00\x01\x58'

relay_port_on='\x55\x01\x01\x02\x02\x02\x02\x5F'
relay_port_off='\x55\x01\x01\x01\x01\x01\x01\x5B'
serial_port='/dev/ttyUSB0'

if [ -e /dev/ttyUSB0 ]
then
    chown root:root /dev/ttyUSB0
fi
sleep 3
if [ -e /dev/ttyUSB1 ]
then
    chown root:root /dev/ttyUSB1
    sleep 2
    chmod 0666 /dev/ttyUSB1
    sleep 2
    echo -e $relay_port_on > /dev/ttyUSB1
fi
sleep 5

LOG=sleep_wakeup.log
cat /dev/null > $LOG
chmod 0666 $serial_port

reset_relay(){
    echo -e $relay_port_off > $serial_port
}

click_power_button(){
    echo -e $relay_port_on > $serial_port
	sleep 0.2
    echo -e $relay_port_off > $serial_port
}

i=1
#LOOP=50000
reset_relay
#while [ $i -le $LOOP ]
while true
do
    click_power_button
	sleep 60
    click_power_button
	sleep 15
	echo "------> Sleep_Wakeup LOOP $i" | tee -a $LOG
	let i=i+1
done
