#!/bin/bash
date=`date "+%Y-%m-%d"`
commands="rsync -avz $date tester@cts-autotest-logserver:~/Autotest_Log/"
expect -c "
    spawn $commands;
    expect {
        \"continue connecting\" {set timeout 5; send \"yes\r\"; exp_continue}
        \"password:\" {send \"qazwsx\r\"}
    }
    set timeout -1
    expect EOF
"
