#!/bin/bash
#devices=`adb devices|grep -w device|awk {'print $1'}`
devices=$1

for id in $devices
do
{
    adb -s $id wait-for-device
    sleep 2
    until [[ `adb -s ${id} shell getprop sys.boot_completed | tr -d '\r\n'` == 1 ]]
    do
        sleep 2
    done
    sleep 5


    if [[ `adb -s $id shell getprop ro.build.version.release | awk -F. '{printf("%d",$1)}'` == 5 ]]
    then
        if [[ `adb -s $id shell getprop persist.sys.language | tr -d '\r\n'` != "en" ]]
        then
            echo "------> set $id language to English"
            adb -s ${id} shell setprop persist.sys.language en
            sleep 1
            adb -s ${id} reboot
            adb -s $id wait-for-device
            sleep 2
            until [[ `adb -s ${id} shell getprop sys.boot_completed | tr -d '\r\n'` == 1 ]]
            do
                sleep 2
            done
        fi
        sleep 5
    fi


    adb -s $id shell input keyevent 26
    sleep 2
    if [[ `adb -s $id shell cat /sys/class/leds/lcd-backlight/brightness | awk '{printf("%d",$1)}'` == 0 ]]
    then
        adb -s $id shell input keyevent 26
        sleep 2
    fi
    sleep 5

    if [[ `adb -s $id shell dumpsys window | grep mFocusedWindow | awk -F/ '{print $(NF-1)}' | awk '{printf("%s",$NF)}'` == "com.google.android.setupwizard" ]]
    then
        if [[ `adb -s $id shell dumpsys window displays | grep init | awk -Fx '{print $1}' | awk -F= '{printf("%d",$NF)}'` -ge 1080 ]]
        then
            #1080P
            echo "------> DUT $id Display: 1080P"
            if [[ `adb -s ${id} shell getprop ro.build.product | tr -d '\r\n' | awk -F_ '{printf("%s",$1)}'` == "Sf3gr" ]]
            then
                # 3GR 1080P
                adb -s $id shell input tap 890 1710
                sleep 1
                adb -s $id shell input tap 120 1710
                sleep 1
                adb -s $id shell input tap 120 140
                adb -s $id shell input tap 890 140
                adb -s $id shell input tap 890 1710
                adb -s $id shell input tap 120 1710
                sleep 3
            else
                # 3GX 1080P
                adb -s $id shell input tap 980 1810
                sleep 1
                adb -s $id shell input tap 110 1810
                sleep 1
                adb -s $id shell input tap 110 100
                adb -s $id shell input tap 980 100
                adb -s $id shell input tap 980 1810
                adb -s $id shell input tap 110 1810
                sleep 3
            fi
        elif [[ `adb -s $id shell dumpsys window displays | grep init | awk -Fx '{print $1}' | awk -F= '{printf("%d",$NF)}'` -ge 720 ]]
        then
            # 720P
            echo "------> DUT $id Display: 720P"
            adb -s $id shell input tap 695 1206
            sleep 1
            adb -s $id shell input tap 65 1206
            sleep 1
            adb -s $id shell input tap 65 75
            adb -s $id shell input tap 695 106
            adb -s $id shell input tap 695 1206
            adb -s $id shell input tap 65 1206
            sleep 3
        else
            echo ""
        fi
    fi

    adb -s $id push UiAutomator.jar /data/local/tmp
    # adb -s $id push media_source/audio /sdcard/
    # adb -s $id push media_source/video /sdcard/
    # adb -s $id shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///mnt/sdcard/

    sleep 3
    if [[ `adb -s $id shell getprop ro.build.version.release | awk -F. '{printf("%d",$1)}'` == 5 ]]
    then
        echo "------> DUT $id Android Version: L"
        echo "------> DUT $id: setup wizard and settings"
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidLWizard1">/dev/null 2>&1
        sleep 5
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidLWizard2">/dev/null 2>&1
        sleep 5
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.InitSettings">/dev/null 2>&1
    else
        echo "------> DUT $id Android Version: M"
        echo "------> DUT $id: setup wizard and settings"
        if [[ `adb -s ${id} shell getprop persist.sys.locale | tr -d '\r\n'` == "zh-CN" ]]
        then
            echo "------> set $id language to English"
            adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidMSetup">/dev/null 2>&1
        else
            adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidMWizard1">/dev/null 2>&1
            sleep 5
            adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidMWizard2">/dev/null 2>&1
            sleep 5
            adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.InitSettings">/dev/null 2>&1
        fi
    fi


    adb -s $id wait-for-device root
    sleep 3
    adb -s $id disable-verity
    adb -s $id wait-for-device
    sleep 2
    adb -s $id reboot
    echo "------> The DUT $id disable-verity done and reboot"

    adb -s $id wait-for-device
    sleep 3
    until [[ `adb -s ${id} shell getprop sys.boot_completed | tr -d '\r\n'` == 1 ]]
    do
       sleep 2
    done
    adb -s $id wait-for-device root
    sleep 3
    adb -s $id wait-for-device remount
    sleep 3
    adb -s $id shell "rm -rf /system/app/Camera2/Camera2.apk"
    adb -s $id shell "rm -rf /system/app/RefCam2/RefCam2.apk"
    adb -s $id shell "rm -rf /system/app/MSMClient/MSMClient.apk"
    adb -s $id shell "rm -rf /system/app/GoogleCamera/GoogleCamera.apk"
    adb -s $id reboot
    echo "------> Removed DUT $id apks and reboot "

    adb -s $id wait-for-device
    sleep 3
    until [[ `adb -s ${id} shell getprop sys.boot_completed | tr -d '\r\n'` == 1 ]]
    do
       sleep 2
    done

    adb -s $id wait-for-device root
    sleep 3
    adb -s $id shell "rm -rf mnt/sdcard/logs/*"
    adb -s $id shell "rm -rf /data/logs/aplog*"
    adb -s $id shell "rm -rf /data/logs/crashlog*"
    adb -s $id shell "rm -rf /data/logs/core/*"
    adb -s $id shell "echo -n "" > /data/logs/history_event"
    adb -s $id shell "rm -rf /mnt/extSdCard/Coredump/*"
    adb -s $id shell "rm -rf /storage/sdcard1/Coredump/*"
    echo "------> The DUT $id clean logs done"

    if [[ `adb -s $id shell getprop ro.build.version.release | awk -F. '{printf("%d",$1)}'` == 5 ]]
    then
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidLWizard1">/dev/null 2>&1
        sleep 2
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidLWizard2">/dev/null 2>&1
    else
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidMWizard1">/dev/null 2>&1
        sleep 2
        adb -s $id shell "uiautomator runtest UiAutomator.jar -c com.intel.AndroidMWizard2">/dev/null 2>&1
    fi
}&
done
wait
