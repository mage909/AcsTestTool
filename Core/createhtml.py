import os
import ConfigParser
import time
from html import HTML


h = HTML("html")
# comment_crash = ["IPANIC", "TOMBSTONE", "UIWDT", "JAVACRASH", "COREDUMP"]
crash_types = ["IPANIC", "COREDUMP", "UIWDT", "ABNORMAL_REBOOT", "TOMBSTONE", "JAVACRASH", "ANR"]
top_line = ["Bench", "Device ID", "Code Branch", "Platform", "Crash", "MAX Test Time", "Board State", "Test Case", "Comments"]
host_password = "qazwsx"
windows_log_server_path = r'\\ccr\ec\proj\iag\ccg\cce\Artifactory\Autotest_Log'
removed_apks = "Camera2 RefCam2 MSMClient GoogleCamera"


def get_bench_info():
    username = os.popen("who | head -n 1 | awk '{print $1}'").read().strip()
    if not username:
        username = 'tester'
    hostname = os.popen("hostname").read().strip()
    ip_address = os.popen("ifconfig | grep 'inet addr' | grep -v 127.0.0.1 | awk '{print $2}' | awk -F : '{print $NF}'").read().strip()
    return "user:%s<br>host:%s<br>ip:%s<br>passwd:%s<br>" % (username, hostname, ip_address, host_password)


bench_info = get_bench_info()


def head_line(table):
    # tr = table.tr(bgcolor="Green")
    tr = table.tr(bgcolor="#00B050")
    for i in top_line:
        tr.th(i)


def str2html(strings):
    return strings.replace('\n', '<br>')


def _handlecount(issue_type, count):
    if count > 0 and issue_type not in ("JAVACRASH", "ANR"):
        return "<span id='fail'>%s x %s</span>" % (issue_type, str(count))
    else:
        return "%s x %s" % (issue_type, str(count))


def format_count(crashs):
    if crashs:
        crash_count = []
        for i in crashs:
            crash_count.append(_handlecount(i['crashtype'], i['count']))
        return '<br>'.join(crash_count)
    else:
        return '<br>'.join(crash + ' x' for crash in crash_types)


def format_boardstate(boardstate, crashdetail):
    if boardstate in ('system hang', 'UI hang', 'recovery mode'):
        return "<span id='failure'>%s</span>" % boardstate
    elif boardstate in ('adb disconnection', 'adb offline', 'charger mode'):
        return "<span id='block'>%s</span>" % boardstate
    elif boardstate == 'normal':
        if crashdetail and any(crashdetail[i]['count'] for i in range(4)):
            return "<span id='block'>%s</span>" % boardstate
        else:
            return "<span id='pass'>%s</span>" % boardstate
    else:
        return boardstate


def format_comments(crashs):
    if crashs:
        comments = []
        for i in crashs:
            if i['crashtype'] in ('IPANIC', 'UIWDT', 'COREDUMP') and i['detail']:
                details = []
                for j in i['detail']:
                    details.append(j['crashlog'] + '<br>' + str2html(j['data']))
                format_details = "<b>%s</b><br>" % i['crashtype'] + '<br>'.join(details) + '<br>'
                comments.append(format_details)
            elif i['crashtype'] == 'TOMBSTONE' and i['detail']:
                tombstones = {}
                for j in i['detail']:
                    if j['data']:
                        tombstones[j['data']] = j['crashlog']
                details = []
                for t, crashlog in tombstones.iteritems():
                    details.append(t + '--' + crashlog)
                format_tombstone = "<b>%s</b><br>" % i['crashtype'] + '<br>'.join(details) + '<br>'
                comments.append(format_tombstone)
            elif i['crashtype'] == 'JAVACRASH' and i['detail']:
                crashlogs = ','.join(c['crashlog'] for c in i['detail'])
                format_javacrash = "<b>%s</b><br>system_server<br>%s<br>" % (i['crashtype'], crashlogs)
                comments.append(format_javacrash)
            else:
                pass
        return '<br>'.join(comments)
    else:
        return ''


def add_row(table, DUT_result):
    bench = bench_info
    sn = DUT_result['ID']
    branch = DUT_result['Branch']
    platform = DUT_result['Platform'].replace('#', '<br>')
    boardstate = format_boardstate(DUT_result['BoardState'], DUT_result['Crash'])
    uptime = DUT_result['MaxTime']
    crash_count = format_count(DUT_result['Crash'])
    testcase = DUT_result['CaseName']
    comments = format_comments(DUT_result['Crash'])
    tr = table.tr()
    test_rst = [bench, sn, branch, platform, crash_count, uptime, boardstate, testcase, comments]
    for i in test_rst:
        new_line = tr.th(" ", id="dev")
        new_line.text(str(i), escape=False)


def handle_url(url):
    if 'jenkins' in url:
        return 'http://' + '/'.join(url.split('/')[2:-3])
    elif url != '':
        usl_slice = url.split('/')
        if not all(usl_slice):
            usl_slice[1] = '/'
        return '/'.join(usl_slice[0:-1])
    else:
        return url


def get_stress_info(path, result):
    taskid = result['taskid']
    stressinfo = ConfigParser.ConfigParser()
    stressinfo.read(os.path.join(path, 'stressinfo.ini'))
    if stressinfo.has_section('stressinfo'):
        image_url = handle_url(stressinfo.get('stressinfo', 'url'))
        casename = stressinfo.get('stressinfo', 'casename')
    else:
        image_url = ''
        casename = ''
    summary = "Here is the %s <b>%s</b> stress test result" % (result['devices'][-1]["Branch"], casename)
    today = time.strftime('%Y-%m-%d', time.localtime())
    DUTconfig = ConfigParser.ConfigParser()
    DUTconfig.read(os.path.join(path, 'DUTs.ini'))
    hostname = os.popen("hostname").read().strip()
    dir_list = (windows_log_server_path, today, "%s_%s" % (hostname, taskid))
    log_path = '\\'.join(dir_list)
    sw = '<b>SW:</b><a href="%s">%s</a>' % (image_url, image_url)
    logpath = '<b>Log Path:</b><a href="%s">%s</a>' % (log_path, log_path)
    rapk = "<b>Removed apks:</b> %s" % removed_apks
    return summary+"<br>"+rapk+"<br>"+sw+"<br>"+logpath+"<br><br>"


def createHTML(result, htmlpath):
    body = h.body()
    body.style('''
    table, th, td
    {
        border: 1px solid black;
        border-collapse: collapse;
    }
    #dev {font-weight:normal;}
    #fail {color:red}
    #pass {background-color:chartreuse}
    #block {background-color:yellow}
    #failure {background-color:red}

    th,td
    {
        padding: 5px;
        font-size:88%
    }
    ''')
    body.text(get_stress_info(htmlpath, result), escape=False)
    table = body.table(style="width:90%")
    head_line(table)
    for DUT_result in result['devices']:
        add_row(table, DUT_result)
    with open(os.path.join(htmlpath, "result.html"), "w") as f:
        f.writelines(h)
