#!/bin/bash
adb -s $1 install mxplayer.apk
adb -s $1 push media /sdcard/Movies
adb -s $1 shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///mnt/sdcard/
#adb -s $1 shell am start com.mxtech.videoplayer.ad/.ActivityMediaList
sleep 3
adb -s $1 shell "uiautomator runtest UiAutomator.jar -c com.intel.VideoPlayback"
