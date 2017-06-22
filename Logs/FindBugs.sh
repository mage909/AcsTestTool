#!/bin/bash
dirs=`ls -d */`
#dirs=`ls -d */ | awk {'print $1'}`
for dir in $dirs
do
    cd ${dir}/data_logs
	echo -----------------------------${dir}--------------------------------------
	echo -n MaxTime:
	if [ `grep -c REBOOT history_event` -gt 20 ]
	then
        grep -c REBOOT history_event
	else
	    grep UPTIME history_event | awk '{print substr($NF,3)}' | sort -r | head -n 1
	fi
	echo -n IPANIC:
	grep -c IPANIC history_event
	echo -n UIWDT:
	grep -c UIWDT history_event
	echo -n TOMBSTONE:
	grep -w TOMBSTONE history_event | grep -c crashlog
	echo -n REBOOT:
	grep -c REBOOT history_event
	echo -n ANR:
	grep ANR history_event  | grep -c crashlog
	echo -n JAVACRASH:
	grep -w JAVACRASH history_event | grep -c crashlog
	echo -n coredump:
	cd ..
	if [ -d Coredump ]
	then
	    ls Coredump | grep -i -c istp 
	else
		echo 0
	fi
	cd data_logs
   
	ipanic=`grep -w IPANIC history_event | grep crashlog | awk -F '/' '{print $5}'`
	echo -----------IPANIC----------
	for i in $ipanic
	do
        if [ -d $i ]
		then
		    echo IPANIC-$i
            grep ^DATA[012] $i/crashfile | awk -F "=" '{print $2}' | xargs echo
		fi
	done

	uiwdt=`grep -w UIWDT history_event | grep crashlog | awk -F '/' '{print $5}'`
	echo -----------UIWDT-----------
	for u in $uiwdt
	do
        if [ -d $u ]
		then
		    echo UIWDT-$u
			grep ^DATA[012] $u/crashfile | awk -F "=" '{print $2}' | xargs echo
		fi
	done

	tombstone=`grep -w TOMBSTONE history_event | grep crashlog | awk -F '/' '{print $5}'`
	echo ---------TOMBSTONE---------
	#echo -n "" > tmp
	for t in $tombstone
	do
        if [ -d $t ]
		then
		    sed -n '5,1p' $t/tombstone_* | awk -F '>>>' '{print $2}' | awk '{printf("%s",$1)}'
			echo "---${t}"
		fi
	done
	#grep -v UNKNOWN tmp | sort | uniq
	#rm -rf tmp

	java_crash=`grep -w JAVACRASH history_event | grep crashlog | awk -F '/' '{print $5}'`
	echo -----------JAVACRASH-system_server-----------
	for j in $java_crash
	do
        if [ -d $j ] && [[ `head -n 1 $j/*crash* | grep system_server | wc -l` > 0 ]]
		then
			echo $j		    
		fi
	done

	cd ../..
done
