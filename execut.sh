
#kill any old process running
killall bf_switchd
killall run_switchd


#load module if not loaded
bf_kdrv_mod_load $SDE_INSTALL

#Compile PIPO-TG p4 code
/$SDE/../tools/p4_build.sh files/pipoTG.p4

# Start the switch
/$SDE/run_switchd.sh -p pipoTG &
sleep 20


#Config PORTS
/$SDE/run_bfshell.sh -f files/portConfig.txt 


#Install RULES
nohup python3 files/tableEntries.py > log &

#rate-show
/$SDE/run_bfshell.sh -f files/view


killall bf_switchd


