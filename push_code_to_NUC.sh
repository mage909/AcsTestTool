#!/bin/bash
for i in `seq 1 13`;
do
    commands="rsync -avz auto_tester tester@autotest-${i}.sh.intel.com:~"
    expect -c "
        spawn $commands;
        expect {
            \"continue connecting\" {set timeout 5; send \"yes\r\"; exp_continue}
            \"password:\" {send \"qazwsx\r\"}
        }
        set timeout -1
        expect EOF
    "
done
