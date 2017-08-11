#!/bin/sh
monkey -p com.eebbk.synmath -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_math.txt 2>&1
monkey -p  com.eebbk.synchinese-s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0  --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_chinese.txt 2>&1
monkey -p com.eebbk.syncenglish -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_synenglish.txt 2>&1
monkey -p com.eebbk.vision -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_vision.txt 2>&1
monkey -p com.eebbk.vtraining -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_vtraining.txt 2>&1
monkey -p com.eebbk.questiondatabase -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_question.txt 2>&1
monkey -p com.eebbk.bbkmiddlemarket -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/monkey_market.txt 2>&1
monkey -p com.eebbk.englishtalk -s 23 --throttle 100  --pct-syskeys 0 --pct-anyevent 0 --pct-appswitch 10 --ignore-timeouts --ignore-crashes -v 100000 > /sdcard/talk_monkey.txt 2>&1