#!/usr/bin/env python3
from subprocess import Popen, PIPE
import subprocess, pwd
import os, time, sys
import atexit

def exit_handler(_pid):
    os.system("kill -9 {}".format(_pid))

my_env = os.environ
my_env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]
#from zigbee_ble_channelization import *
#scan_time = 60*30 #+ 11.6#16*3 # takes about up to 8min to discover 10 of our devices
#startup_extra_time = 9
devices = 1

print("argv0 "+sys.argv[0])
print("argv1 "+sys.argv[1])
try:
    noise = str(sys.argv[1])
except:
    #print("Assuming proto=zigbee")
    noise = '-10'

TRIALS =  [0] #[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]#range(0,100,1)#[0,1,2,3,4,5,6,7,8,9]#range(10,100,1)#[0,1,2,3,4,5,6,7,8,9] # range(10,100,1)#
NOISES = [-15,-14,-13,-12] #[0,1,2]#,0.1,3]#[1,2,3]#,2,3,4,5,6]#,2,4,8,16,32]#[0.1,1,3]
PERS = [] # ZIG=False
TIMEOUT = 10 # roughly each second is one pakcket
# BLE=True
# LORA=False

#user_name, cwd = my_args[:2]
user_name = "gnuradio"
#args = my_args[2:]
pw_record = pwd.getpwnam(user_name)
user_name      = pw_record.pw_name
user_home_dir  = pw_record.pw_dir
user_uid       = pw_record.pw_uid
user_gid       = pw_record.pw_gid
env = os.environ.copy()
env[ 'HOME'     ]  = user_home_dir
env[ 'LOGNAME'  ]  = user_name
#env[ 'PWD'      ]  = cwd
env[ 'USER'     ]  = user_name
#report_ids('starting ' + str(args))
# https://stackoverflow.com/questions/1770209/run-child-processes-as-different-user-from-a-long-running-python-process/6037494#6037494
def demote(user_uid, user_gid):
    def result():
        report_ids('starting demotion')
        os.setgid(user_gid)
        os.setuid(user_uid)
        report_ids('finished demotion')
    return result


def report_ids(msg):
    print('uid, gid = %d, %d; %s' % (os.getuid(), os.getgid(), msg))


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
          os.system("rm nohup.out")
          subp1 = Popen(['nohup','./apps/single_user/tx_rx_simulation.py','-e',str(nois)],) 
#                        preexec_fn=demote(user_uid, user_gid),) # env=env)
          # -f /proc/<pid>/fd/1
          atexit.register(exit_handler, subp1.pid)          
          print("starting flowgraph pid {}".format(subp1.pid))
          time.sleep(TIMEOUT) # this is crutial !!!!! otherwise report is nothing
          #os.system('cat nohup.out')
#          os.system("cat /proc/{}/fd/1 | grep -c 'CRC valid'; cat /proc/{}/fd/1 | grep -c Frame".format(subp1.pid,subp1.pid))
          #os.system("cat nohup.out | grep -c 'CRC valid'; cat nohup.out | grep -c Frame")
          # _pass = subprocess.run("cat nohup.out | grep -c 'CRC valid';".split(' '), stdout=subprocess.PIPE)
          # _fail = subprocess.run("cat nohup.out | grep -c 'Frame';".split(' '), stdout=subprocess.PIPE)
          _pass=0;_total=0;_per=1;
          with open("nohup.out", "r") as fp:
              for line in fp:
                if "CRC valid" in line:
                    _pass = _pass +1
                if "Frame" in line:
                    _total = _total +1

          print("PER="+str(_pass)+'/'+str(_total))
          if _total!=0:
            _per = (_total-_pass)/_total
            print('='+str(_per))
          PERS.append(_per)
          os.system("kill -9 {}".format(subp1.pid))
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
