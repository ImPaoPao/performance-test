#!/bin/sh
echo "APP Start"
workdir=/data/local/tmp/launch
workout=${workdir}/out
exe_log=${workdir}/out/exe_log
touch ${exe_log}
mkdir -p ${workdir}
mkdir -p ${workout}
trackfile=${workdir}/track
busybox=${workdir}/busybox
function launcher() {
    while read line
    do
        params=(${line})
        apkpath=`pm path ${params[0]}`
        apkinfo=(`du -k ${apkpath:8}`)
        apksize=${apkinfo[0]}
        resultdir=${workout}/${params[0]}
        mkdir -p ${resultdir}
        echo ${resultdir}
        resultxml=${resultdir}/$1.xml
	logfile=${resultdir}/log.txt
        touch ${resultxml}
	touch ${logfile}
        echo ${resultxml} > ${logfile}
        echo "<?xml version=\"1.0\" encoding=\"utf-8\"?>" > ${resultxml}
        echo "<result name=\"${params[0]}\" size=\"${apksize}\">" >> ${resultxml}
        OLD_IFS="${IFS}"
        IFS=","
        activities=(${params[1]})
        IFS="${OLD_IFS}"
        for activity in ${activities[@]}
        do
	    echo ${params[0]},${activity}>>${exe_log}
            echo ${params[0]}>>${logfile}
            echo ${activity}>>${logfile}
            i=0
            times=0
            while ((${i}<${params[3]}))
            do
                i=$((${i}+1))
                if [ -f ${trackfile} ] && [ "`cat ${trackfile}`" != "done" ]; then
                    totalTime=`${busybox} timeout -t 5 am start -W ${params[0]}/${activity} |grep -E "TotalTime: .+"`
		    echo "time=",${totalTime}>>${exe_log}
                    totalTime=(${totalTime})
                    if [ times -eq 0 ];then
                        times=${totalTime[1]}
                    else
                        times=${times}","${totalTime[1]}
                    fi
                    if [ $1 == "cool" ]; then
			echo "cool">>${exe_log}
			echo "cool">>${logfile}
			sleep 5
                        am force-stop ${params[0]}
			sleep 5
			am kill-all
			sleep 10
                    fi
                    input keyevent 3
                    sleep 5
                fi
            done
            echo ${times}>>${logfile}
	    echo ${times}>>${exe_log}
            echo "  <time name=\"${activity}\">"${times}"</time>" >> ${resultxml}
        done
        echo "</result>" >> ${resultxml}
    done < ${workdir}/$1.txt
}

case $1 in
	"start")
		echo 'cool start:'>${exe_log}
		launcher cool
		echo 'warm start:'>>${exe_log}
		launcher warm
		echo "done">${trackfile}
		;;
esac
