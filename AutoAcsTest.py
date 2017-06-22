'''
    usage: sudo python AutoAcsTest.py image_url case_name
'''
import sys
import os
import re
import time
import subprocess
import ConfigParser
# from Core.CleanUp import cleanUp
# from Core.CopyImage import copy_fls
from multiprocessing import Pool
from Core.DownLoad import download
from Core.FlashCtrl import flashCtrl
from Core.DUTstate import restart_adb_sever
from Core.relay import Relay
from Stress_Case.stresscase import sleep_wakeup, coldboot, antutu, factory_reset, audio_playback
from Stress_Case.stabilitycase import run



case_name_list = ("monkey", "monkey_apks", "warmboot", "coldboot", "sleep_wakeup", "video_playback", "idle", "customized_monkey", "bt_on_off", "wifi_on_off", "camera_record", "camera_capture", "camera_switch", "audio_playback", "antutu", "factory_reset")
url = sys.argv[1].strip()
case_name = sys.argv[2].strip().lower()
if case_name not in case_name_list:
    print "Parameter error,there have not this stress name: %s" % case_name
    sys.exit(0)
if case_name == "customized_monkey":
    monkey_cmd = sys.argv[3]
elif case_name in ("antutu", "factory_reset", "bt_on_off", "wifi_on_off", "camera_record", "camera_capture", "camera_switch", "video_playback"):
    if sys.argv[3].isdigit():
        loop = sys.argv[3]
    else:
        print "------> please input currect loop number."
        sys.exit()
if not any(url.endswith(suffix) for suffix in ('zip', 'tar', 'tar.gz', '7z')):
    print "The image url error,image url:%s" % url
    sys.exit(0)
pattern = re.compile(r'/(\d+)/')
urlslice = re.findall(pattern, url)
if len(urlslice) > 0:
    buildNo = urlslice[0]
else:
    buildNo = ''
acs_root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
imge_dir = os.path.join(acs_root_dir, "Image")
flash_tool_dir = os.path.join(acs_root_dir, "FlashTool")
precondition_dir = os.path.join(acs_root_dir, "PreCondition")
stress_dir = os.path.join(acs_root_dir, "Stress_Case")
monkey_dir = os.path.join(stress_dir, "Monkey")
videoplayback_dir = os.path.join(stress_dir, "videoplayback")

# read DUTs config
DUTconfig = ConfigParser.ConfigParser()
DUTconfig.read(os.path.join(acs_root_dir, "DUTs.ini"))
devices = DUTconfig.sections()
DUT_relayPort = {}
for d in devices:
    DUT_relayPort[d] = DUTconfig.get(d, 'RelayPort')

# write stress info to stressinfo.ini
stressconfig = ConfigParser.ConfigParser()
stressconfig.add_section('stressinfo')
stressconfig.set('stressinfo', 'URL', sys.argv[1])
stressconfig.set('stressinfo', 'BuildNo', buildNo)
stressconfig.set('stressinfo', 'CaseName', case_name)
with open(os.path.join(acs_root_dir, 'stressinfo.ini'), 'w') as f:
    stressconfig.write(f)

# clean Up
print "------> Clean up image folder"
# cleanUp(imge_dir, IncludeStr=[".fls", ".zip", ".img","mvconfig", "elf", ".json"], ExceptStr="")
os.system("rm -rf %s" % os.path.join(imge_dir, r'*'))
# Download image
download(url, imge_dir)
# copy image
# copy_fls("./", "./")
# flash Image
mrelay = Relay()
time.sleep(5)
flashCtrl(mrelay, imge_dir, flash_tool_dir, DUT_relayPort, buildNo)
print "------> Flash DUTs done,setup %s test environment" % case_name
# cleanUp(imge_dir,IncludeStr=[".fls",".zip",".img","mvconfig","elf",".json"],ExceptStr="")
devices = ""
for sn in DUT_relayPort.keys():
    devices = devices + sn + " "
devices = devices.strip()
setupProcess = subprocess.Popen(["./DUT_Setup.sh", devices], cwd=precondition_dir)
for i in range(40):
    time.sleep(30)
    if setupProcess.poll() is not None:
        break
    elif i == 39:
        setupProcess.kill()

# clean temp files
os.system("rm -rf %s" % os.path.join(stress_dir, r'*.log'))
os.system("rm -rf %s" % os.path.join(monkey_dir, r'*.log'))
os.system("rm -rf %s" % os.path.join(monkey_dir, r'*.txt'))

# restart adb server
# print "------> Restart adb server"
# restart_adb_sever()

# run stress test
print "------> Setup done,run %s stress test" % case_name
os.chdir(stress_dir)
if case_name == "monkey":
    monkey_process_list = []
    for i in DUT_relayPort.keys():
        monkey_process_list.append(subprocess.Popen(["./monkey.sh", i], cwd=monkey_dir))
    for p in monkey_process_list:
        p.wait()
elif case_name == "monkey_apks":
    monkey_apks_process_list = []
    for i in DUT_relayPort.keys():
        monkey_apks_process_list.append(subprocess.Popen(["./monkey_apk.sh", i], cwd=monkey_dir))
    for p in monkey_apks_process_list:
        p.wait()
elif case_name == "warmboot":
    warmboot_process_list = []
    for i in DUT_relayPort.keys():
        warmboot_process_list.append(subprocess.Popen(["./warmboot.sh", i], cwd=stress_dir))
    for p in warmboot_process_list:
        p.wait()
elif case_name == "coldboot":
    # coldboot_process = subprocess.Popen(["./coldboot.sh"], cwd=stress_dir)
    # coldboot_process.wait()
    coldboot(mrelay)
elif case_name == "sleep_wakeup":
    # sleep_wakeup_process = subprocess.Popen(["./sleep_wakeup.sh"], cwd=stress_dir)
    # sleep_wakeup_process.wait()
    sleep_wakeup(mrelay)
elif case_name == "video_playback":
    video_playback_process_list = []
    for i in DUT_relayPort.keys():
        video_playback_process_list.append(subprocess.Popen(["./video_playback.sh", i], cwd=videoplayback_dir))
    for p in video_playback_process_list:
        p.wait()
elif case_name == "idle":
    pass
elif case_name == "customized_monkey":
    cmonkey_process_list = []
    for i in DUT_relayPort.keys():
        cmonkey_process_list.append(subprocess.Popen(["./customized_monkey.sh", i, monkey_cmd], cwd=monkey_dir))
    for p in cmonkey_process_list:
        p.wait()
elif case_name == "antutu":
    pools = Pool(processes=4)
    for i in DUT_relayPort.keys():
        pools.apply_async(antutu, args=(i, loop))
    pools.close()
    pools.join()
elif case_name == "factory_reset":
    pools = Pool(processes=4)
    for i in DUT_relayPort.keys():
        pools.apply_async(factory_reset, args=(i, loop, precondition_dir))
    pools.close()
    pools.join()
elif case_name == "audio_playback":
    pools = Pool(processes=4)
    for i in DUT_relayPort.keys():
        pools.apply_async(audio_playback, args=(i,))
    pools.close()
    pools.join()
else:
    pools = Pool(processes=4)
    for i in DUT_relayPort.keys():
        pools.apply_async(run, args=(i, case_name, loop))
    pools.close()
    pools.join()
