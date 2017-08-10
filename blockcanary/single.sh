#!/bin/sh

workdir=/data/local/tmp/blockcanary
workout=${workdir}/out

mkdir -p ${workout}

function monitor() {
    sleep 600
    if [ "$(echo `uiautomator dump 2>&1`)" == "ERROR: null root node returned by UiTestAutomationBridge." ] ;then
        am force-stop ${1}
    fi
}

case $1 in
"start")
    pid=$$
    while read line
    do
        params=(${line})
        package=${params[0]}
        packout=${workout}/${package}
        if [ ! -d ${packout} ] ;then
            mkdir -p ${packout}
            monitor ${package} &
            mpid=$!
            echo ${pid} ${mpid} > ${workdir}/pid
            if [ ${params[4]} -eq 1 ] ;then
                monkey -p ${package} -s ${params[3]} --throttle ${params[2]} --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v ${params[1]} > ${packout}/single.txt 2>&1
            elif [ ${params[4]} -eq 0 ] ;then
                monkey -p ${package} -s ${params[3]} --throttle ${params[2]} --pct-syskeys 0 --pct-anyevent 0 -v ${params[1]} > ${packout}/monkey.txt 2>&1
            fi
            kill -9 ${mpid}
            am force-stop ${package}
        fi
    done < ${workdir}/choice.txt
    echo "done" >> ${workdir}/track
    ;;
"stop")
    echo `${workdir}/busybox pidof com.android.commands.monkey` >> ${workdir}/pid
    kill -9 `cat ${workdir}/pid`
    echo "done" >> ${workdir}/track
    ;;
"done")
    ;;
esac
