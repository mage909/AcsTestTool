import time
import os


def waitUi(interval, iteration, serialNumber=None):
    for i in range(iteration):
        if serialNumber is None:
            result_ui = os.popen(
                "adb shell getprop sys.boot_completed").read()
        else:
            result_ui = os.popen(
                "adb -s %s shell getprop sys.boot_completed" % serialNumber).read()

        time.sleep(interval)
        if "1" in result_ui:
            print "device boot state: %s" % result_ui
            return True
            break
        elif i == iteration - 1:
            print "------> device boot to ui fail"
            return False
        else:
            print "----> Retry to boot to ui %s times" % i
            # usb_disConnect("two")
            # time.sleep(10)
            # usb_Connect("two")


def waitAdb(serialNumber=None):
    time.sleep(3)
    if serialNumber is None:
        result_adb = os.popen("adb get-state").read()
    else:
        result_adb = os.popen("adb -s %s get-state" % serialNumber).read()
    if "device" in result_adb and os.popen("timeout 5 adb -s %s shell getprop ro.serialno" % serialNumber).read().strip() == serialNumber:
        print "------> DUT-%s : adb connect success" % serialNumber
        return True
    else:
        print "------> DUT-%s : adb connect fail" % serialNumber
        return False


def get_buildNo(serialNumber=None):
    if serialNumber is None:
        rtn = os.popen("adb shell getprop ro.build.version.incremental").read().strip()
    else:
        rtn = os.popen("adb -s %s shell getprop ro.build.version.incremental" % serialNumber).read().strip()
    return rtn.split('-')[-1]


def checkState(serialNumber):
    DUT_state = os.popen("adb -s %s get-state" % serialNumber).read().strip()
    if DUT_state == 'unknown':
        return 'adb disconnection'
    elif DUT_state == 'offline':
        return 'adb offline'
    elif DUT_state == 'recovery':
        return 'recovery mode'
    elif DUT_state == 'device':
        if os.system("timeout 10 adb -s %s shell getprop ro.serialno >/dev/null" % serialNumber):
            return 'system hang'
        elif os.popen("adb -s %s shell getprop ro.bootmode" % serialNumber).read().strip() == 'charger':
            return 'charger mode'
        elif os.system("timeout 10 adb -s %s shell monkey 1 >/dev/null" % serialNumber) or "is the system running?" in os.popen("timeout 10 adb -s %s shell monkey 1" % serialNumber).read():
            return 'UI hang'
        else:
            return 'normal'
    else:
        return 'adb disconnection'


def handle_DUT(serialNumber, state):
    if state in ('recovery mode', 'charger mode'):
        os.system("adb -s %s reboot" % serialNumber)


def restart_adb_sever():
    time.sleep(3)
    os.system("adb kill-server")
    time.sleep(3)
    os.system("adb start-server")
    time.sleep(3)
