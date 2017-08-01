#!/bin/bash
echo on
workdir=/data/local/tmp/module
workout=${workdir}/out
mkdir -p ${workout}
trackfile=${workdir}/track
datadir=/sdcard/performance-test
exe_log=${workdir}/module_log
touch ${exe_log}
echo $1
echo $1 >> ${exe_log}
case $1 in
	"start")
		echo $$ > ${workdir}/pid
		pm install -r ${workdir}/performance-test.apk
		pm install -r ${workdir}/performance.apk
		while read line
		do
			params=(${line})
			echo ${params}>> ${exe_log}
			test_package=${params[0]}
			test_case=${params[1]}
			test_method=${params[2]}
			test_number=${params[3]}
			test_count=${params[4]}
			source_package=${params[5]}
			test_type=${params[6]}
			sys_num=${params[7]}
			app_num=${params[8]}
			#if [${test_count} -gt 0];then
			mkdir -p ${datadir}/${test_number}
			echo ${test_method} >> ${trackfile}
			mkdir -p ${workout}/${test_number}
			am instrument -w -r  -e number ${test_number} -e mpackage ${source_package} -e type ${test_type} -e appnum ${app_num} -e class ${test_package}.${test_case}\#${test_method} -e count ${test_count} com.eebbk.test.performance.test/android.support.test.runner.AndroidJUnitRunner>${workout}/${test_number}/instrument.txt
			#kill -9 ${lpid}
			#kill -9 ${tpid}
			sleep 3
			cp -f ${datadir}/${test_number}/* ${workout}/${test_number}
			cp -f ${datadir}/${test_number}/result.xml ${workout}/${test_number}
			#cp -f /sdcard/log.txt ${workout}/${test_number}
			#cp -f /sdcard/top.txt ${workout}/${test_number}
			sleep 5
		done < ${workdir}/choice.txt
		echo "done" >> ${trackfile}
		;;
	"stop")
		kill -9 `cat ${workdir}/pid`
		am force-stop com.eebbk.test.performance.test
		am force-stop com.eebbk.test.performance
		echo "done" >> ${trackfile}
		;;
	"done")
		pm uninstall com.eebbk.test.performance.test
		pm uninstall com.eebbk.test.performance
		pm uninstall com.eebbk.test.kit
		pm uninstall com.eebbk.test.kit.test
		;;
esac

