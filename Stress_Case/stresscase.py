#!/usr/bin/env pyhon
# -*- coding: UTF-8 -*-
import time
import os
import subprocess


def sleep_wakeup(mrelay):
    mrelay.allOutOn(flag=1)
    time.sleep(5)
    with open('sleep_wakeup.log', 'w') as f:
        i = 1
        while True:
            # screen off
            mrelay.allOutOn()
            time.sleep(0.2)
            mrelay.allOutOff()
            # sleep 60s
            time.sleep(60)
            # screen on
            mrelay.allOutOn()
            time.sleep(0.2)
            mrelay.allOutOff()
            # wake 15s
            time.sleep(15)
            print "------> Sleep_Wakeup LOOP %d" % i
            f.write("------> Sleep_Wakeup LOOP %d\n" % i)
            f.flush()
            i += 1


def coldboot(mrelay):
    mrelay.allOutOn(flag=1)
    time.sleep(5)
    with open('coldboot.log', 'w') as f:
        i = 1
        while True:
            # power off
            mrelay.allOutOn()
            time.sleep(15)
            mrelay.allOutOff()
            # sleep 10s
            time.sleep(10)
            # power on
            mrelay.allOutOn()
            time.sleep(6)
            mrelay.allOutOff()
            # wait DUT boot
            time.sleep(90)
            print "------> ColdBoot Loop %d" % i
            f.write("------> ColdBoot Loop %d\n" % i)
            f.flush()
            i += 1


def factory_reset(sn, loop, setup_path):
    with open("factory_reset_%s.log" % sn, 'w') as f:
        for i in range(1, int(loop)+1):
            os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.FactoryReset >/dev/null 2>&1" % sn)
            print "------> DUT %s: run factory reset,loop %d" % (sn, i)
            f.write("factory reset loop %d\n" % i)
            f.flush()
            time.sleep(5*60)
            subprocess.call(["./wizard_setup.sh", sn], cwd=setup_path)


def antutu(sn, loop):
    time.sleep(3)
    os.system("adb -s %s install AnTuTu-Benchmark_v5.7.1.apk" % sn)
    time.sleep(2)
    with open("antutu_%s.log" % sn, 'w') as f:
        for i in range(1, int(loop)+1):
            os.system("adb -s %s shell am start -n com.antutu.ABenchMark/.ABenchMarkStart" % sn)
            time.sleep(15)
            os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.Antutu >/dev/null 2>&1" % sn)
            print "------> DUT %s: run antutu benchmark,loop %d" % (sn, i)
            f.write("antutu loop %d\n" % i)
            f.flush()
            print "------> sleep 5min,wait for antutu benchmark result"
            time.sleep(5*60)
            os.system("adb -s %s shell input keyevent 4" % sn)
            time.sleep(1)
            os.system("adb -s %s shell input keyevent 4" % sn)
            time.sleep(1)
            os.system("adb -s %s shell input keyevent 3" % sn)
            time.sleep(3)


def audio_playback(sn):
    os.system("adb -s %s root" % sn)
    time.sleep(5)
    os.system("timeout 10 adb -s %s wait-for-device" % sn)
    if os.system("timeout 10 adb -s %s shell getprop ro.serialno >/dev/null" % sn):
        print "------> system hang,or adb shell unavailable,exit"
    os.system("adb -s %s push media_source/audio /sdcard/" % sn)
    os.system("adb -s %s shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///mnt/sdcard/" % sn)
    time.sleep(2)
    os.system("adb -s %s shell am start com.google.android.music/com.android.music.activitymanagement.TopLevelActivity" % sn)
    time.sleep(5)
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.AudioPlayback >/dev/null 2>&1" % sn)


if __name__ == '__main__':
    # factory_reset('000009', '5', '/home/jenkins/android_dev/AcsTestTool/PreCondition')
    audio_playback("4455490")
