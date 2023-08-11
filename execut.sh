killall bf_switchd
killall run_switchd
source /home/admin12/bf-sde-9.9.0/tools/set_sde.bash
bf_kdrv_mod_load $SDE_INSTALL
/home/admin12/tools/p4_build.sh files/pipoTG.p4
/home/admin12/bf-sde-9.9.0/run_switchd.sh -p pipoTG &
sleep 20


#Config PORTS
/home/admin12/bf-sde-9.9.0/run_bfshell.sh -f files/portConfig.txt 



#Install RULES
nohup python3 files/tableEntries.py > log &

#Config PORTS
/home/admin12/bf-sde-9.9.0/run_bfshell.sh -f files/view

#python3 -m p4runtime_sh --grpc-addr 127.0.0.1:9090 \
#  --device-id 0 --election-id 0,1 --config <p4info.txt>,<pipeline config>
