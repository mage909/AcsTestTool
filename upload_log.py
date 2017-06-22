#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import os
import sys
import subprocess
import datetime
import calendar

logserver_path = '/media/windows_logserver'
root_path = sys.path[0]
LOCAL = 'local'
SERVER = 'server'
# upload file size's fault tolerant value
# if abs(server_file_size - local_file_size) > 10M, upload it
FAULT_VALUE = 10


def get_strftoday():
    return time.strftime("%Y-%m-%d", time.localtime())


def get_filesize(filepath):
    return os.popen("du -s %s | awk '{print $1}'" % filepath).read().strip()


def format_filesize(filesize):
    return str(int(filesize)/1024) + 'M'


def get_abspath(flag, *filenames):
    if flag == 'local':
        return os.path.join(root_path, *filenames)
    elif flag == 'server':
        return os.path.join(logserver_path, *filenames)


def get_files(flag, strdate):
    log_path = get_abspath(flag, strdate)
    if os.path.exists(log_path):
        return {f: get_filesize(get_abspath(flag, strdate, f)) for f in os.listdir(log_path)}
    else:
        return {}


def rm_premonth_log(now):
    dayscount = datetime.timedelta(days=now.day)
    preday = now - dayscount
    premonth = preday.strftime("%Y-%m-")
    premonth_log = get_abspath(LOCAL, premonth) + '*'
    subprocess.call("rm -rf %s" % premonth_log, shell=True)


def get_upload_files(lfiles, sfiles):
    local_files_set = set(lfiles.keys())
    server_files_set = set(sfiles.keys())
    common_files = local_files_set & server_files_set
    diff_files = local_files_set - server_files_set
    upload_files = list(diff_files)
    for i in common_files:
        if abs(int(lfiles[i])/1024 - int(sfiles[i])/1024) > FAULT_VALUE:
            upload_files.append(i)
    return upload_files


def waitfile(filepath):
    filesize = get_filesize(filepath)
    while True:
        time.sleep(10)
        if get_filesize(filepath) != filesize:
            filesize = get_filesize(filepath)
        else:
            return True


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def upload_log():
    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    # rm last month log files
    if now.day == calendar.monthrange(now.year, now.month)[-1] and now.hour > 23:
        print "[%s] rm local last month logs" % get_current_time()
        rm_premonth_log(now)

    server_files = get_files(SERVER, today)
    str_server_files = str({f: format_filesize(server_files[f]) for f in server_files})
    print "[%s] server files:%s" % (get_current_time(), str_server_files)

    local_files = get_files(LOCAL, today)
    str_local_files = str({f: format_filesize(local_files[f]) for f in local_files})
    print "[%s] local files:%s" % (get_current_time(), str_local_files)

    upfiles = get_upload_files(local_files, server_files)
    if upfiles:
        for i in upfiles:
            waitfile(get_abspath(LOCAL, today, i))
            # upload file
            server_path = get_abspath(SERVER, today)
            if not os.path.exists(server_path):
                os.mkdir(server_path)
            print "[%s] upload %s to log server" % (get_current_time(), i)
            subprocess.call("cp -r %s %s" % (get_abspath(LOCAL, today, i), server_path), shell=True)


if __name__ == '__main__':
    while True:
        upload_log()
        print "[%s] sleep 5 minutes" % get_current_time()
        print "-------------------------------------I'm dividing line-----------------------------------------------"
        time.sleep(5 * 60)
