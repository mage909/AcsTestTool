import os
import re
from fnmatch import fnmatch
from DUTstate import checkState


def rmStrSpaces(strings):
    return re.sub(r' {2,}', ' ', strings)


def __getCaseTpye(logpath):
    '''
    usage: __getCaseTpye('/home/jenkins/Logs/2016-02-02/autotest-8_65')
    '''
    files = os.listdir(logpath) if os.path.exists(logpath) else []
    if any(name for name in files if fnmatch(name, 'warmboot_*.log')):
        return 'warmboot'
    elif 'sleep_wakeup.log' in files:
        return 'sleep_wakeup'
    elif 'coldboot.log' in files:
        return 'coldboot'
    else:
        return 'time'


def getAliveDevice():
    devices = os.popen("adb devices | grep -w device | awk '{print $1}'").read().split()
    aliveDUTs = []
    for d in devices:
        if checkState(d) == 'normal':
            aliveDUTs.append(d)
    return aliveDUTs


def __getHistoryEventMaxTime(filePath):
    '''
    usage: __getHistoryEventMaxTime('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001/data_logs/history_event')
    '''
    MaxTime = []
    currentUptime = os.popen("head -n 1 %s | awk '{print $NF}'" % filePath).read().strip()
    MaxTime.append(currentUptime[2:])
    uptimeList = os.popen("grep -w UPTIME %s | awk '{print $NF}'" % filePath).readlines()
    if len(uptimeList):
        for t in uptimeList:
            MaxTime.append(t.strip()[2:])
    return sorted(MaxTime)[-1]


def getMaxTime(DUTlogpath, casename):
    '''
    usage: getMaxTime('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001', 'monkey')
    '''
    history_event = os.path.join(DUTlogpath, 'data_logs', 'history_event')
    isExists = os.path.exists(history_event)
    root_logpath = os.path.dirname(DUTlogpath)
    sn = os.path.basename(DUTlogpath)

    if casename == 'warmboot':
        f = os.path.join(root_logpath, "warmboot_%s.log" % sn)
        if os.path.exists(f):
            loop = os.popen("grep -i warmboot %s | tail -n 1 | awk '{print $NF}'" % f).read().strip()
            return "Loop:" + loop
    elif casename == 'coldboot':
        if isExists:
            loop = os.popen("grep REBOOT %s | wc -l" % history_event).read().strip()
            return "Loop:" + loop
    elif casename in ('sleep_wakeup', 'antutu', 'factory_reset'):
        f = os.path.join(root_logpath, "%s.log" % casename)
        if os.path.exists(f):
            loop = os.popen("tail -n 1 %s | awk '{print $NF}'" % f).read().strip()
            return "Loop:" + loop
    elif casename in ('bt_on_off', 'wifi_on_off', 'camera_record', 'camera_capture', 'camera_switch'):
        f = os.path.join(root_logpath, "%s_%s.result" % (casename, sn))
        if os.path.exists(f):
            pass_ = os.popen("grep -i pass %s | wc -l" % f).read().strip()
            fail_ = os.popen("grep -i fail %s | wc -l" % f).read().strip()
            return "Pass:" + pass_ + " Fail:" + fail_
    else:
        if isExists:
            return __getHistoryEventMaxTime(history_event)
    return ''


def getCount(DUTlogpath, issuetype, casename):
    '''
    usage: getCount('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001', 'IPANIC')
    '''
    history_event = os.path.join(DUTlogpath, 'data_logs', 'history_event')
    coredump_dir = os.path.join(DUTlogpath, 'Coredump')
    if os.path.exists(history_event):
        if issuetype == 'IPANIC':
            return int(os.popen('grep -c IPANIC %s' % history_event).read().strip())
        elif issuetype == 'COREDUMP':
            if os.path.exists(coredump_dir):
                return int(os.popen('ls %s | grep -i -c istp' % coredump_dir).read().strip())
        elif issuetype == 'UIWDT':
            return int(os.popen('grep -c UIWDT %s' % history_event).read().strip())
        elif issuetype == 'ABNORMAL_REBOOT':
            if casename in ('coldboot', 'warmboot'):
                return 0
            else:
                return int(os.popen('grep -c REBOOT %s' % history_event).read().strip())
        elif issuetype == 'TOMBSTONE':
            return int(os.popen('grep -w TOMBSTONE %s | grep -c crashlog' % history_event).read().strip())
        elif issuetype == 'JAVACRASH':
            return int(os.popen('grep -w JAVACRASH %s | grep -c crashlog' % history_event).read().strip())
        elif issuetype == 'ANR':
            return int(os.popen('grep ANR %s | grep -c crashlog' % history_event).read().strip())
    return 0


def __getIssueCrashlog(filepath, issueType):
    '''__getIssueCrashlog('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001/data_logs/history_event', 'IPANIC')
    '''
    crashlogs = os.popen("grep -w %s %s | grep crashlog | awk -F '/' '{print $NF}'" % (issueType, filepath)).readlines()
    return [crashlog.strip() for crashlog in crashlogs]


def __getCoredumpLineSN(filepath):
    '''
    usage: __getCoredumpLineSN('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001/Coredump/xxxx.istp')
    '''
    startLineSN = [26]
    endLineSN = 50
    with open(filepath, 'rb') as f:
        for i in range(25):
            _ = f.readline()
        for i in range(26, 50):
            data = f.readline()
            if 'Trap in ' in data:
                startLineSN.append(i)
            elif 'IA gp regs:' in data:
                endLineSN = i - 2
                break
    startLineSN = startLineSN[0] if len(startLineSN) == 1 else startLineSN[1]
    return (startLineSN, endLineSN)


def __getCoredumpData(filepath):
    '''
    usage: __getCoredumpData('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001/Coredump/xxxx.istp')
    '''
    startLineSN, endLineSN = __getCoredumpLineSN(filepath)
    data = []
    coredumpType = ''
    with open(filepath, 'rb') as f:
        for i in range(startLineSN-1):
            _ = f.readline()
        firstLine = f.readline()
        data.append(firstLine)
        coredumpType = firstLine.split()[-1]
        for i in range(startLineSN, endLineSN):
            data.append(f.readline())
    return (coredumpType, ''.join(data))


def getLocalApps():
    aliveDUTs = getAliveDevice()
    if len(aliveDUTs):
        appslist = os.popen('adb -s %s shell pm list packages -s' % aliveDUTs[0]).readlines()
        return [appname.strip().split(':')[-1] for appname in appslist]
    else:
        return []


def __parseTomstoneType(tombstone):
    if tombstone:
        tomlist = tombstone.split('.')
        if tombstone.lower() == 'unknown':
            return ('unknown', 'Medium')
        elif 'system_server' in tombstone:
            return ('system_server', 'Critical')
        elif '/system/bin' in tombstone:
            return ('/system/bin/*', 'High')
        elif tombstone.lower() in ('grep', 'android', 'google'):
            return ('local app', 'Medium')
        elif len(tomlist) > 1 and tomlist[1] in ('google', 'intel', 'android'):
            return ('local app', 'Medium')
        else:
            return ('3rd app', 'Low')
    else:
        return ('', '')


def getIssueDetails(logpath, issuetype):
    '''
    usage: getIssueDetails('/home/jenkins/Logs/2016-02-02/autotest-8_65/000001', 'IPANIC')
    '''
    detail = []
    history_event = os.path.join(logpath, 'data_logs', 'history_event')
    if os.path.exists(history_event):
        pass
    else:
        return detail

    if issuetype == 'IPANIC':
        crashlogs = __getIssueCrashlog(history_event, 'IPANIC')
        for c in crashlogs:
            issue = {}
            issue['issuetype'] = 'IPANIC'
            issue['crashlog'] = c
            issue['severity'] = 'Critical'
            crashfile = os.path.join(logpath, 'data_logs', c, 'crashfile')
            if os.path.exists(crashfile):
                ipanicdata = os.popen('grep ^DATA[012] %s' % crashfile).read()
                issue['data'] = rmStrSpaces(ipanicdata)
            else:
                issue['data'] = ''
            detail.append(issue)
        return detail
    elif issuetype == 'COREDUMP':
        coredumpPath = os.path.join(logpath, 'Coredump')
        coredumps = os.popen("ls %s | grep -i istp" % coredumpPath).read().split()
        for c in coredumps:
            issue = {}
            issue['crashlog'] = c
            issue['severity'] = 'Critical'
            if os.path.getsize(os.path.join(coredumpPath, c)):
                issue['issuetype'], issue['data'] = __getCoredumpData(os.path.join(coredumpPath, c))
            else:
                issue['issuetype'] = '0kb'
                issue['data'] = ''
            detail.append(issue)
        return detail
    elif issuetype == 'UIWDT':
        crashlogs = __getIssueCrashlog(history_event, 'UIWDT')
        for c in crashlogs:
            issue = {}
            issue['issuetype'] = 'UIWDT'
            issue['crashlog'] = c
            issue['severity'] = 'Critical'
            crashfile = os.path.join(logpath, 'data_logs', c, 'crashfile')
            if os.path.exists(crashfile):
                uiwdtdata = os.popen('grep ^DATA[012] %s' % crashfile).read()
                issue['data'] = rmStrSpaces(uiwdtdata)
            else:
                issue['data'] = ''
            detail.append(issue)
        return detail
    elif issuetype == 'TOMBSTONE':
        crashlogs = __getIssueCrashlog(history_event, 'TOMBSTONE')
        for c in crashlogs:
            issue = {}
            issue['crashlog'] = c
            crashlog = os.path.join(logpath, 'data_logs', c)
            if os.path.exists(crashlog):
                issue['data'] = os.popen("sed -n '5,1p' %s/tombstone_* | awk '{print $(NF-1)}'" % crashlog).read().strip()
            else:
                issue['data'] = ''
            issue['issuetype'], issue['severity'] = __parseTomstoneType(issue['data'])
            detail.append(issue)
        return detail
    elif issuetype == 'JAVACRASH':
        crashlogs = __getIssueCrashlog(history_event, 'JAVACRASH')
        for c in crashlogs:
            crashlog = os.path.join(logpath, 'data_logs', c)
            if os.path.exists(crashlog):
                filesList = os.listdir(crashlog)
                system_server_file = [name for name in filesList if fnmatch(name, '*crash*.txt')]
                if len(system_server_file):
                    if fnmatch(system_server_file[0], 'system_server*.txt') or os.popen('head -n 1 %s | grep system_server ' % os.path.join(crashlog, system_server_file[0])).read().strip():
                        issue = {}
                        issue['issuetype'] = 'system_server'
                        issue['crashlog'] = c
                        issue['severity'] = 'Critical'
                        issue['data'] = ''
                        detail.append(issue)
        return detail

    return []
