#!/usr/bin/env bash

if [ $# -lt 1 ];then
    echo "please input the device ID,the script exit."
    exit 1
fi
_id=$1
_log_file="monkey_apks_${1}.log"

# Number of monkey inputs
_ninputs=20000000

log_date() {
    echo "["`date +%Y-%m-%d\ %H:%M:%S`"] $@"
}

#install apks
./install.sh $_id

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
	# adb -s $_id shell 'echo 0 > /d/watchdog/kernel_watchdog/enable'
	# adb -s $_id shell 'echo 0 > /d/watchdog/vmm_scu_wdt_enable'
    log_date "[$_cnt]"
    _cnt=$(($_cnt + 1))
    # Unlock
    adb -s $_id shell 'input keyevent' 3
    # Execute monkey
    log_date "[monkey -v $_ninputs]"
    adb -s $_id shell " monkey -v-v --ignore-crashes --ignore-timeouts --kill-process-after-error --ignore-security-exceptions --throttle 1000 -v $_ninputs">> "$_log_file"
    adb -s $_id wait-for-devices
    sleep 15
done
