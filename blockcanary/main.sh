#!/bin/sh

workdir=/data/local/tmp/blockcanary
workout=${workdir}/out

mkdir -p ${workout}

choicefile=${workdir}/choice.txt
errorignore="--ignore-timeouts --ignore-crashes"
pkgmsg="--pkg-whitelist-file"

case $1 in
"start")
    echo $$ > ${workdir}/pid
    if [ $5 -eq 0 ] ;then
        for line in `pm list package -3`
        do
            echo ${line:8} >> ${choicefile}
        done
        pkgmsg="--pkg-blacklist-file"
    fi
    if [ $6 -eq 0 ] ;then
        errorignore=""
    fi
    if [ -f ${choicefile} ] ;then
        monkey -s $2 --throttle $3 --pct-syskeys 0 --pct-anyevent 0 ${errorignore} ${pkgmsg} ${choicefile} -v $4 > ${workout}/blockcanary.txt 2>&1
    else
        monkey -s $2 --throttle $3 --pct-syskeys 0 --pct-anyevent 0 ${errorignore} -v $4 > ${workout}/blockcanary.txt 2>&1
    fi
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
