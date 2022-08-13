#!/usr/bin/env python3
from subprocess import Popen, PIPE
import subprocess, pwd
import os, time, sys, io
import atexit

def exit_handler(_pid):
    os.system("kill -9 {}".format(_pid))
TRIALS =  [0] #[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]#range(0,100,1)#[0,1,2,3,4,5,6,7,8,9]#range(10,100,1)#[0,1,2,3,4,5,6,7,8,9] # range(10,100,1)#
NOISES = [-15,-14,-13,-12] #[0,1,2]#,0.1,3]#[1,2,3]#,2,3,4,5,6]#,2,4,8,16,32]#[0.1,1,3]
PERS = [] # ZIG=False
TIMEOUT = int(sys.argv[1]) # roughly each second is one pakcket

import re

_surrogates = re.compile(r"[\uDC80-\uDCFF]")

def detect_decoding_errors_line(l, _s=_surrogates.finditer):
    """Return decoding errors in a line of text

    Works with text lines decoded with the surrogateescape
    error handler.

    Returns a list of (pos, byte) tuples

    """
    # DC80 - DCFF encode bad bytes 80-FF
    return [(m.start(), bytes([ord(m.group()) - 0xDC00]))
            for m in _s(l)]

for trial in TRIALS:
  for nois in NOISES:

        # DIR = "data/"+proto
        # os.system("mkdir "+DIR)
        # DIR = DIR + "/aug3"
        # os.system("mkdir "+DIR)
        # DIR = DIR+"/ch_{}_dev_{}/".format(channel_time,devices)
        # os.system("mkdir "+DIR)

        # if proto == 'multi':
        #  print(my_env)
          #os.system("mv nohup.out nohup"+str(nois)+".out")
          subp1 = Popen(['./apps/single_user/tx_rx_simulation.py','-e',str(nois)],) 
#                        preexec_fn=demote(user_uid, user_gid),) # env=env)
          # -f /proc/<pid>/fd/1
          time.sleep(TIMEOUT) # this is crutial !!!!! otherwise report is nothing
          #print("cp /proc/{}/fd/1 nohup.out".format(subp1.pid))
          os.system("cp /proc/{}/fd/1 nohup.out".format(subp1.pid))
          os.system("mv nohup.out nohup"+str(nois)+".out")
          atexit.register(exit_handler, subp1.pid)
          os.system("kill -9 {}".format(subp1.pid))
          #print("starting flowgraph pid {}".format(subp1.pid))
#          _now = time.time() + TIMEOUT  #
          # time.sleep(TIMEOUT) # this is crutial !!!!! otherwise report is nothing
          #os.system('cat nohup.out')
#          os.system("cat /proc/{}/fd/1 | grep -c 'CRC valid'; cat /proc/{}/fd/1 | grep -c Frame".format(subp1.pid,subp1.pid))
          #os.system("cat nohup.out | grep -c 'CRC valid'; cat nohup.out | grep -c Frame")
          # _pass = subprocess.run("cat nohup.out | grep -c 'CRC valid';".split(' '), stdout=subprocess.PIPE)
          # _fail = subprocess.run("cat nohup.out | grep -c 'Frame';".split(' '), stdout=subprocess.PIPE)
          _pass=0;_total=0;_per=1;
          #with open("nohup.out", "r") as fp:
          with io.open("nohup"+str(nois)+".out", "r", encoding="utf-8",errors="surrogateescape") as fp:
              for i,line in enumerate(fp):
                errors = detect_decoding_errors_line(line)
                if errors:
                  print(f"Found errors on line {i}:")
                  for (col, b) in errors:
                    print(f" {col + 1:2d}: {b[0]:02x}")
                  continue

                if "CRC valid" in line:
                    _pass = _pass +1
                if "Frame" in line:
                    _total = _total +1
#                time.sleep(1)
#                if (time.time() >= _now):
#                    break

          print("PER="+str(_pass)+'/'+str(_total))
          if _total!=0:
            _per = (_total-_pass)/_total
            print('='+str(_per))
          PERS.append(_per)
          #os.system("kill -9 {}".format(subp1.pid))
          # top_block_cls=zigbee_ble_channelization
          # tb = top_block_cls()
          # tb.start()
  print(NOISES)
  print(PERS)
#             #'{}'.format(devices),'{}'.format(channel_time)])
#           # time.sleep(scan_time+5)
#           subp2 = Popen(['sudo','operf', '--pid='+str(subp1.pid),'--callgraph']) # os.getpid()
#           print("sudo operf --pid={} --callgraph".format(subp1.pid))
#           time.sleep(5)
# #          subp2.kill()
#           #os.system("sudo kill -9 {}".format(subp2.pid))
#           os.system("sudo killall -9 operf")
#           #subp3 = Popen(['opreport','-l','|','grep','xlating'])
#           os.system("opreport -l | grep xlating")
#           os.system("opreport -l | grep xlating | awk '{print $2}' ")
          # os.system("kill -9 $!")
          # #os.system("sudo kill -9 {}".format(subp1.pid))
          # os.system('cat res_lora_sim.txt | grep -c "CRC valid"')
          # os.system('cat res_lora_sim.txt | grep -c "Frame"')
          

          # tb.stop()
          # tb.wait()
          # subp1.wait()
          # os.system("mv zig_act_scan.pcap zig_act_scan{}.pcap".format(trial))
          # os.system("mv zig_act_scan{}.pcap ".format(trial)+DIR)

          # subp1 = Popen(['python3','zig_passive.py','{}'.format(devices),'{}'.format(channel_time)])
          # #time.sleep(scan_time+5)
          # #os.system("kill -9 {}".format(subp1.pid))
          # subp1.wait()
          # os.system("mv zig_simple_scan.pcap zig_simple_scan{}.pcap".format(trial))
          # os.system("mv zig_simple_scan{}.pcap ".format(trial)+DIR)
