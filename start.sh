#!/bin/bash
echo "Start.sh"
timeout=200
sleep_for=1

#REPO=gr-lora_sdr/
#BRANCH=experimental/gr-3.8/multi-stream-gateway
REPO=gr-lora_tapparelj
BRANCH=master

#cd /home/gnuradio/${REPO}
#git checkout ${BRANCH}
#cd build
#cmake ../
#make
#sudo make install
#sudo ldconfig

# /home/gnuradio/start.sh
#nohup /home/gnuradio/lora_RX_feather_915.py 2>&1 > /home/gnuradio/res.txt & #uhd_usrp_probe
echo "tx_rx_simulation.py -e ${1}"
nohup ./apps/single_user/tx_rx_simulation.py -e ${1} 2>&1 > res_lora_sim.txt &
_pid=$!

function jumpto
{
PASS=`cat res_lora_sim.txt | grep -c "CRC valid"`
TOTAL=`cat res_lora_sim.txt | grep -c "Frame"`
echo "PASS"
echo $PASS
echo "TOTOAL"
echo $TOTAL
#PER=`echo 1-$PASS/$TOTAL | genius`
#echo "PER"
#echo $PER
kill -9 $_pid
}

sleep 7 & # this should take care of startup delay even if usrp is used

find_process=$(ps aux | grep -v "grep" | grep "sleep")

while [ ! -z "$find_process" ]; do
    find_process=$(ps aux | grep -v "grep" | grep "sleep")

    if [ "$timeout" -le "0" ]; then
      echo "Timeout"
      jumpto
      exit 1
    fi

    timeout=$(($timeout - $sleep_for))
    sleep $sleep_for
done

function jumpto
{
PASS=`cat res_lora_sim.txt | grep -c "CRC valid"`
TOTAL=`cat res_lora_sim.txt | grep -c "Frame"`
echo "PASS"
echo $PASS
echo "TOTOAL"
echo $TOTAL
PER=$((PASS/TOTAL))
echo "PER"
echo $PER

kill -9 $_pid
}
exit 0

# #!/usr/bin/env bash

# cd /home/gnuradio/gr-lora_sdr/build
# cmake ../
# make
# sudo make install
# sudo ldconfig
# # /home/gnuradio/start.sh
# python3 /home/gnuradio/lora_RX_feather_915.py #uhd_usrp_probe

