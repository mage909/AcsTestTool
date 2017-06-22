import os
import time
import thread
# from glob import glob
from fnmatch import fnmatch
from DUTstate import waitAdb
from DUTstate import get_buildNo


def adbCmd(t, serialNumber):
    time.sleep(3)

    if serialNumber is None:
        time.sleep(t)
        os.system("timeout 10 adb reboot")
    else:
        time.sleep(t)
        os.system("timeout 10 adb -s %s reboot" % serialNumber)


def get_fls_str(fls_path):
    files = os.listdir(fls_path)
    fls = [name for name in files if fnmatch(name, "*.fls")]
    mvconfig_fls = [name for name in fls if fnmatch(name, "mvconfig*")]
    if len(mvconfig_fls) == 1:
        keep_fls = mvconfig_fls[0]
    elif "mvconfig_smp.fls" in mvconfig_fls:
        keep_fls = "mvconfig_smp.fls"
    elif "mvconfig_smp_signed.fls" in mvconfig_fls:
        keep_fls = "mvconfig_smp_signed.fls"
    elif "mvconfig_smp_64bit.fls" in mvconfig_fls:
        keep_fls = "mvconfig_smp_64bit.fls"
    elif "mvconfig_smp_64bit_signed.fls" in mvconfig_fls:
        keep_fls = "mvconfig_smp_64bit_signed.fls"
    else:
        keep_fls = ""
    mvconfig_fls.remove(keep_fls)
    for i in mvconfig_fls:
        fls.remove(i)
    abs_fls = [os.path.join(fls_path, name) for name in fls]
    fls_str = " ".join(abs_fls)
    return fls_str


def flash(fls_str, tool_path):
    return os.system("sudo {0}/DownloadTool --library={0}/libDownloadTool.so --erase-mode 0 {1} >/dev/null".format(tool_path, fls_str))


# def flash(fls_path, tool_path):
#     files = os.listdir(fls_path)
#     fls = [name for name in files if fnmatch(name, "*.fls")]
#     if "mvconfig_smp.fls" in fls:
#         # Sofia 3GR L 32bit
#         retn = os.system("sudo {1}/DownloadTool --library={1}/libDownloadTool.so --erase-mode 0 {0}/psi_flash.fls {0}/slb.fls {0}/mobilevisor.fls {0}/boot.fls {0}/cache.fls {0}/mvconfig_smp.fls {0}/recovery.fls {0}/secvm.fls {0}/splash_img.fls {0}/system.fls {0}/ucode_patch.fls {0}/userdata.fls >/dev/null".format(fls_path, tool_path))
#     elif "mvconfig_smp_64bit.fls" in fls:
#         # Sofia 3GR L 64bit
#         retn = os.system("sudo {1}/DownloadTool --library={1}/libDownloadTool.so --erase-mode 0 {0}/psi_flash.fls {0}/slb.fls {0}/mobilevisor.fls {0}/boot.fls {0}/cache.fls {0}/mvconfig_smp_64bit.fls {0}/recovery.fls {0}/secvm.fls {0}/splash_img.fls {0}/system.fls {0}/ucode_patch.fls {0}/userdata.fls >/dev/null".format(fls_path, tool_path))
#     elif "oem_signed.fls" in fls:
#         # Sofia 3GR M
#         retn = os.system("sudo {1}/DownloadTool --library={1}/libDownloadTool.so --erase-mode 0 {0}/psi_flash_signed.fls {0}/vrl_signed.fls {0}/slb_signed.fls {0}/mobilevisor_signed.fls {0}/boot_signed.fls {0}/cache_signed.fls {0}/fwu_image.fls {0}/mvconfig_smp_signed.fls {0}/oem_signed.fls {0}/recovery_signed.fls {0}/secvm_signed.fls {0}/splash_img_signed.fls {0}/system_signed.fls {0}/ucode_patch_signed.fls {0}/userdata_signed.fls >/dev/null".format(fls_path, tool_path))
#     else:
#         # Sofia 3GX
#         retn = os.system("sudo {1}/DownloadTool --library={1}/libDownloadTool.so --erase-mode 0 {0}/psi_flash_signed.fls {0}/vrl_signed.fls {0}/slb_signed.fls {0}/mobilevisor_signed.fls {0}/boot_signed.fls {0}/cache_signed.fls {0}/mvconfig_smp_signed.fls {0}/recovery_signed.fls {0}/secvm_signed.fls {0}/splash_img_signed.fls {0}/system_signed.fls {0}/ucode_patch_signed.fls {0}/userdata_signed.fls >/dev/null".format(fls_path, tool_path))
#     return retn


def adbCmd_flash(fls_str, tool_path, t, serialNumber):
    thread.start_new_thread(adbCmd, (t, serialNumber))
    rtn = flash(fls_str, tool_path)
    return rtn


def onkey_flash(mrelay, fls_str, tool_path, port, t):
    thread.start_new_thread(mrelay.onkey, (port, t))
    rtn = flash(fls_str, tool_path)
    return rtn


def flashCtrl(mrelay, fls_path, tool_path, DUT_relayPort, buildNo):
    devices = DUT_relayPort.keys()
    image_fls_str = get_fls_str(fls_path)
    for serialNumber in devices:
        if waitAdb(serialNumber):
            print "------> DUT-%s : adb flash" % serialNumber
            if adbCmd_flash(image_fls_str, tool_path, 5, serialNumber) != 0:
                print "------> DUT-%s : adb reboot flash fail, try onkey method." % serialNumber
                onkey_flash(mrelay, image_fls_str, tool_path, DUT_relayPort[serialNumber], 15)
        else:
            print "------> DUT-%s : adb shell unavailable, try onkey method." % serialNumber
            onkey_flash(mrelay, image_fls_str, tool_path, DUT_relayPort[serialNumber], 15)
        time.sleep(10)

    # if buildNo == '':
    #     return 0

    # print "------> Flash done,check the DUT buildNo"
    # for id in devices:
    #     os.system("timeout 60 adb -s %s wait-for-device" % id)
    #     if waitAdb(id) and get_buildNo(id) == buildNo:
    #         print "------> DUT-%s image correct,the buildNo is %s" % (id, buildNo)
    #     else:
    #         print "------> DUT-%s image incorrect,try flash image again" % id
    #         onkey_flash(fls_path, tool_path, DUT_relayPort[id], 15)
    #     time.sleep(10)
