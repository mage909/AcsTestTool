import os
import time
import functools
import sys


def wakeup(sn):
    if os.popen("adb -s %s shell cat /sys/class/leds/lcd-backlight/brightness" % sn).read().strip() == '0':
        os.system("adb -s %s shell input keyevent 26" % sn)


def setup(sn):
    os.system("adb -s %s root" % sn)
    time.sleep(5)
    os.system("timeout 10 adb -s %s wait-for-device" % sn)
    if os.system("timeout 10 adb -s %s shell getprop ro.serialno >/dev/null" % sn):
        print "------> system hang,or adb shell unavailable,exit"
        sys.exit()
    os.system("adb -s %s push media_source/audio /sdcard/" % sn)
    os.system("adb -s %s push media_source/video /sdcard/" % sn)
    os.system("adb -s %s shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///mnt/sdcard/" % sn)


def logwatcher():
    def log_watcher(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            sn = args[0]
            wakeup(sn)
            os.system("adb -s %s shell input keyevent 62" % sn)
            os.system("adb -s %s shell logcat -c" % sn)
            func(*args)
            log = os.popen("adb -s %s shell logcat -d " % sn).read()
            with open("%s_%s.log" % (func.__name__, sn), "w") as f:
                f.writelines(log)
        return wrapper
    return log_watcher


def checkresult(condition_list):
    def check_result(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            casename = func.__name__
            func(*args)
            with open("%s_%s.log" % (func.__name__, args[0]), "r") as f:
                logs = f.readlines()
            if reduce(lambda x, y: x and y, map(lambda x: x in "".join(logs), condition_list)):
                if "playback" in casename:
                    return "PASS"
                else:
                    return {casename: "PASS"}
            else:
                if "playback" in casename:
                    return "FAIL"
                return {casename: "FAIL"}
        return wrapper
    return check_result


@checkresult(["setWifiEnabled: true", "setWifiEnabled: false"])
@logwatcher()
def wifi_on_off(sn):
    os.system("adb -s %s shell svc wifi disable" % sn)
    time.sleep(3)
    os.system("adb -s %s shell svc wifi enable" % sn)
    time.sleep(3)
    os.system("adb -s %s shell svc wifi disable" % sn)
    time.sleep(3)


@checkresult(["Accept thread started", "BluetoothSocket listen thread finished"])
@logwatcher()
def bt_on_off(sn):
    os.system("adb -s %s shell service call bluetooth_manager 6" % sn)
    time.sleep(5)
    os.system("adb -s %s shell service call bluetooth_manager 8" % sn)
    time.sleep(5)
    os.system("adb -s %s shell service call bluetooth_manager 6" % sn)
    time.sleep(3)
    os.system("adb -s %s shell input keyevent 3" % sn)
    time.sleep(2)


@checkresult(["Displayed", ": start", ": reset", "Starting IMAS pcm devices", "Stopping and closing IMAS pcm devices"])
@logwatcher()
def audio_playback(sn, audio):
    os.system("adb -s %s shell am start -a android.intent.action.VIEW -d file:///mnt/sdcard/%s -t audio/*" % (sn, audio))
    time.sleep(40)
    os.system("adb -s %s shell input keyevent 127" % sn)
    time.sleep(3)
    os.system("adb -s %s shell input keyevent 126" % sn)
    time.sleep(3)
    os.system("adb -s %s shell input keyevent 86" % sn)


@checkresult(["Displayed"])
@logwatcher()
def video_playback(sn, video):
    os.system("adb -s %s shell am start -a android.intent.action.VIEW -d file:///mnt/sdcard/%s -t video/*" % (sn, video))
    time.sleep(15)
    os.system("adb -s %s shell input keyevent 127" % sn)
    time.sleep(5)
    os.system("adb -s %s shell input keyevent 126" % sn)
    time.sleep(3)
    os.system("adb -s %s shell input keyevent 4" % sn)
    time.sleep(5)


@checkresult(["switchCamera", "onSwitchCameraStart", "onSwitchCameraEnd"])
@logwatcher()
def camera_switch(sn):
    # os.system("adb -s %s shell am start -a android.media.action.IMAGE_CAPTURE" % sn)
    # os.system("adb -s %s shell am start com.arcsoft.camera2/com.arcsoft.camera.CameraLauncher" % sn)
    # time.sleep(5)
    # switch camera
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.CameraSwitch>/dev/null 2>&1" % sn)
    time.sleep(5)
    # os.system("adb -s %s shell input keyevent 4" % sn)
    # time.sleep(1)
    # os.system("adb -s %s shell input keyevent 4" % sn)


@checkresult(["onCaptureStarted", "onCaptureCompleted", "bCaptureDone: true"])
@logwatcher()
def camera_capture(sn):
    # os.system("adb -s %s shell am start -a android.media.action.IMAGE_CAPTURE" % sn)
    # os.system("adb -s %s shell am start com.arcsoft.camera2/com.arcsoft.camera.CameraLauncher" % sn)
    # time.sleep(5)
    os.system("adb -s %s shell input keyevent KEYCODE_CAMERA" % sn)
    time.sleep(5)
    # switch camera
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.CameraSwitch>/dev/null 2>&1" % sn)
    time.sleep(5)
    os.system("adb -s %s shell input keyevent KEYCODE_CAMERA" % sn)
    time.sleep(5)
    # os.system("adb -s %s shell input keyevent 4" % sn)
    # time.sleep(1)
    # os.system("adb -s %s shell input keyevent 3" % sn)


@checkresult(["stopVideoRecording", "initializeRecorder"])
@logwatcher()
def camera_record(sn):
    # os.system("adb -s %s shell am start -a android.media.action.VIDEO_CAPTURE" % sn)
    os.system("adb -s %s shell am start com.arcsoft.camera2/com.arcsoft.camera.CameraLauncher" % sn)
    time.sleep(5)
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.CameraRecord>/dev/null 2>&1" % sn)
    time.sleep(60)
    os.system("adb -s %s shell input keyevent KEYCODE_CAMERA" % sn)
    time.sleep(5)
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.CameraSwitch>/dev/null 2>&1" % sn)
    time.sleep(5)
    os.system("adb -s %s shell uiautomator runtest UiAutomator.jar -c com.intel.CameraRecord>/dev/null 2>&1" % sn)
    time.sleep(60)
    os.system("adb -s %s shell input keyevent KEYCODE_CAMERA" % sn)
    time.sleep(5)
    os.system("adb -s %s shell input keyevent 4" % sn)
    time.sleep(1)
    os.system("adb -s %s shell input keyevent 3" % sn)


def audio_runner(sn):
    l = ["aac.aac", "flac.flac", "mono.mp3", "ogg.ogg", "pcm.wav", "stereo.mp3"]
    rslt = {}
    for i in l:
        r = audio_playback(sn, i)
        rslt[i] = r
    return rslt


def video_runner(sn):
    l = ["h264.mp4", "mpeg4.mp4", "vp8.webm"]
    rslt = {}
    for i in l:
        r = video_playback(sn, i)
        rslt[i] = r
    return rslt


def run(sn, case, loop):
    setup(sn)
    result_name = "%s_%s.result" % (case, sn)
    if case == 'audio_playback':
        case = 'audio_runner'
    elif case == 'video_playback':
        case = 'video_runner'
    if case in ('camera_switch', 'camera_capture'):
        os.system("adb -s %s shell am start com.arcsoft.camera2/com.arcsoft.camera.CameraLauncher" % sn)
        time.sleep(5)
    with open(result_name, 'w') as f:
        for i in range(int(loop)):
            print "------> DUT %s: %s loop %d" % (sn, case, i+1)
            # f.write("DUT %s: %s loop %d\n" % (sn, case, i+1))
            rst = globals()[case](sn)
            f.write("%s\n" % str(rst))
            f.flush()


if __name__ == "__main__":
    run("445349001", 'camera_capture', '5')
    run("445349001", 'camera_record', '2')
    run("445349001", 'camera_switch', '2')
    run("445349001", 'audio_playback', '2')
    run("445349001", 'bt_on_off', '2')
    run("445349001", 'wifi_on_off', '2')
