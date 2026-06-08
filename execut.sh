#!/bin/bash

killall bf_switchd 2>/dev/null
killall run_switchd 2>/dev/null
killall -f "python3 files/run.py" 2>/dev/null

RUN_PID=""
cleanup() {
    if [ -n "$RUN_PID" ]; then
        kill $RUN_PID 2>/dev/null
        wait $RUN_PID 2>/dev/null
    fi
    killall bf_switchd 2>/dev/null
}
trap cleanup EXIT INT TERM

bf_kdrv_mod_load $SDE_INSTALL

/$SDE/../tools/p4_build.sh files/pipoTG.p4

/$SDE/run_switchd.sh -p pipoTG > switchd.log 2>&1 &
sleep 20

/$SDE/run_bfshell.sh -f files/portConfig.txt

#back terminal to normal state + ESC[H + ESC[2J
stty sane 2>/dev/null || true
printf '^[[H^[[2J'

python3 files/run.py
