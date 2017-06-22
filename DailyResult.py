#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
    usage: sudo python DaliyResult.py taskid
    DUT state:adb disconnection, adb offline, recovery mode, system hang, charger mode, UI hang, normal
'''
import time
import os
import sys
import ConfigParser
import datetime
import requests
import json
import serial
import glob
import subprocess
import pexpect
from Core.DUTstate import checkState, handle_DUT
from Core.result import getMaxTime, getCount, getIssueDetails
from Core.createhtml import createHTML
from Core.sendmail import send_mail


# init
hostname = os.popen("hostname").read().strip()
root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
teardown_dir = os.path.join(root_dir, "TearDown")
root_log_dir = os.path.join(root_dir, "Logs")
stress_dir = os.path.join(root_dir, "Stress_Case")
taskid = sys.argv[1]
today = datetime.date.today().isoformat()
pull_log_path = os.path.join(today, hostname+'_'+taskid)
relay_allout_off = '\xFE\x0F\x00\x00\x00\x04\x01\x00\x71\x92'
os.system("rm -rf %s" % os.path.join(root_dir, '*.html'))


# read stress info
stressinfo = ConfigParser.ConfigParser()
stressinfo.read(os.path.join(root_dir, 'stressinfo.ini'))
if stressinfo.has_section('stressinfo'):
    image_url = stressinfo.get('stressinfo', 'url')
    buildNo = stressinfo.get('stressinfo', 'buildno')
    casename = stressinfo.get('stressinfo', 'casename')
else:
    image_url, casename, buildNo = ''


# read DUTs config
DUTconfig = ConfigParser.ConfigParser()
DUTconfig.read(os.path.join(root_dir, 'DUTs.ini'))
devices = DUTconfig.sections()


print "------> teardown"
os.system("ps aux | grep AutoAcsTest | grep -v color | awk '{print $2}' | xargs kill -9")
# reset relays
get_relays = sorted(glob.glob("/dev/ttyUSB*"))
for t in get_relays:
    os.system("sudo chown root:root %s" % t)
    time.sleep(2)
    os.system("sudo chmod 666 %s" % t)
    time.sleep(2)
    r = serial.Serial(port=t, baudrate=9600, timeout=1)
    time.sleep(2)
    r.write(relay_allout_off)
time.sleep(5)
os.system("%s >/dev/null" % os.path.join(teardown_dir, "tear_down.sh"))
print "------> teardown finished"
print "------> sleep 60s,wait for devices"
time.sleep(60)



# Status of the device include:adb disconnection,adb offline,recovery mode,
# system hang,charger mode,UI hang,normal
print "------> get all DUTs state"
DUT_state = {}
for d in devices:
    state = checkState(d)
    DUT_state[d] = state
    handle_DUT(d, state)
if casename == 'coldboot' and all(s == 'charger mode' for s in DUT_state.values()):
    for i in DUT_state.keys():
        DUT_state[i] = 'normal'
print "------> DUT state:%s" % str(DUT_state)
print "------> get DUTs state done,sleep 60s and wait for devices"
# print DUT_state
time.sleep(60)


os.chdir(root_log_dir)
print "------> pull all DUTs full logs..."
# os.system("./pull_full_logs.sh %s >/dev/null 2>&1" % pull_log_path)
pulllog_process = subprocess.Popen("./pull_full_logs.sh %s >/dev/null 2>&1" % pull_log_path, shell=True)
abs_logpath = os.path.join(root_log_dir, pull_log_path)

def get_filesize(filepath):
    return os.popen("du -s %s | awk '{print $1}'" % filepath).read().strip()

time.sleep(30)
logsize = get_filesize(abs_logpath)
while True:
    time.sleep(30)
    if get_filesize(abs_logpath) != logsize:
        logsize = get_filesize(abs_logpath)
    else:
        try:
            pulllog_process.kill()
        except Exception:
            pass
        break

print "------> pull logs done"
print "------> rsync log to log server(tester@cts-autotest-logserver)"
os.system("./rsync_log.sh >/dev/null")
print "------> rsync log done"



print "------> Prase logs data..."
result = {'taskid': taskid, 'hostname': hostname+'.sh.intel.com', 'devices': []}
issue_type = ('IPANIC', 'COREDUMP', 'UIWDT', 'ABNORMAL_REBOOT', 'TOMBSTONE', 'JAVACRASH', 'ANR')

for d in devices:
    branch = DUTconfig.get(d, 'Branch')
    DUT_log_path = os.path.join(root_log_dir, pull_log_path, d)
    DUT = {'ID': d, 'Branch': branch, 'Platform': DUTconfig.get(d, 'Platform'), 'BoardState': DUT_state[d], 'BuildNo': buildNo, 'URL': image_url, 'CaseName': casename}
    if DUT_state[d] in ('recovery mode', 'charger mode', 'normal', 'UI hang'):
        DUT['MaxTime'] = getMaxTime(DUT_log_path, casename)
        crash = []
        for t in issue_type:
            crash_detail = {}
            crash_detail['crashtype'] = t
            crash_detail['count'] = getCount(DUT_log_path, t, casename)
            if t == 'ABNORMAL_REBOOT' and casename not in ('warmboot', 'coldboot') and DUT_state[d] in ('recovery mode', 'charger mode'):
                crash_detail['count'] = crash_detail['count'] - 1

            if t == 'ANR' or t == 'ABNORMAL_REBOOT' or crash_detail['count'] == 0:
                crash_detail['detail'] = []
            else:
                crash_detail['detail'] = getIssueDetails(DUT_log_path, t)
            crash.append(crash_detail)
        DUT['Crash'] = crash
    else:
        DUT['MaxTime'] = ''
        DUT['Crash'] = []
    result['devices'].append(DUT)
print "------> Prase log data done"




with open(os.path.join(root_dir, 'data.json'), 'w') as f:
    json.dump(result, f)
print "------> Dump josn data"
post_data_json = json.dumps(result)
print "------> Post data to web server"
url = 'http://shctsbdb14.sh.intel.com/api/autotest/android/teardown/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=post_data_json)
if r.status_code != 200:
    time.sleep(10)
    r = requests.post(url, data=post_data_json)
print "------> After post result,the webserver return code: %d" % r.status_code



# create and send result email
createHTML(result, root_dir)
email_subject = "%s stress test report on host: %s" % (casename, hostname)
print "------> Send stress report email"
if r.status_code == 200:
    send_mail(root_dir, sys.argv[2], sys.argv[2], email_subject)
else:
    send_mail(root_dir, sys.argv[2], [sys.argv[2], "linx.ye@intel.com", "kuix.zhao@intel.com"], email_subject, files=[os.path.join(root_dir, 'data.json')])



# send result html to server:tester@shctsbdb14:~/Autotest_Log/email_data
print "------> Send result html to server: tester@shctsbdb14:~/Autotest_Log/email_data"
os.chdir(root_dir)
os.system("mv result.html %s.html" % taskid)
cmd = "scp %s.html tester@shctsbdb14:~/Autotest_Log/email_data/" % taskid
child = pexpect.spawn(cmd, cwd=root_dir)
while True:
    index = child.expect(["(yes/no)", "[Pp]assword", pexpect.TIMEOUT, pexpect.EOF])
    if index == 0:
        child.sendline("yes")
    elif index == 1:
        child.sendline("qazwsx")
        break
    elif index == 2:
        print "------> scp result email timeout"
        child.kill()
        break
    elif index == 3:
        child.kill()
child.expect(pexpect.EOF)
child.close(force=True)
print "------> DaliyResult done."
