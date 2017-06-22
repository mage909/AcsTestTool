#!/usr/bin/env bash
_id=$1
_log_file="monkey_${1}.log"

log_date() {
    echo "["`date +%Y-%m-%d\ %H:%M:%S`"] $@"
}

rm -rf "$_log_file"

./kmsg.sh $_id &
./kmemleak.sh $_id &

#Run monkey in a loop
_cnt=1
while true; do
    adb -s $_id root
    sleep 2
    adb -s $_id wait-for-devices
	sleep 3
    log_date "[Monkey Loop $_cnt]"
    log_date "[$2]"
    _cnt=$(($_cnt + 1))
    # Unlock
    adb -s $_id shell 'input keyevent' 3
    # Execute monkey
    adb -s $_id shell "$2" >> "$_log_file"
    adb -s $_id wait-for-devices
    sleep 15
done
