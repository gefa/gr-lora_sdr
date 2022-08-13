#!/usr/bin/env python3
#from subprocess import Popen, PIPE
import subprocess
import subprocess, pwd
import os, time, sys, io
import atexit
import threading

def exit_handler(_pid):
    os.system("kill -9 {}".format(_pid))
TRIALS =  [0] #[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]#range(0,100,1)#[0,1,2,3,4,5,6,7,8,9]#range(10,100,1)#[0,1,2,3,4,5,6,7,8,9] # range(10,100,1)#
NOISES = [-5,0] #[-15,-14,-13,-12] #[0,1,2]#,0.1,3]#[1,2,3]#,2,3,4,5,6]#,2,4,8,16,32]#[0.1,1,3]
PERS = [] # ZIG=False
TIMEOUT = int(sys.argv[1]) # roughly each second is one pakcket

import re
FNULL = open(os.devnull, "w")
#logfile = open("logfile", "w")
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
def on_timeout(proc, status_dict):
    status_dict['timeout']=True
    print("timed out")
    proc.kill()

for trial in TRIALS:
  for nois in NOISES:
          logfile = open("logfile","w")
          status_dict = {'timeout':False}

          args = ['./apps/single_user/tx_rx_simulation.py','-e',str(nois)]
          subp1 = subprocess.Popen(args, shell=True, universal_newlines=True, stdout=logfile, stderr=FNULL)

          timer = threading.Timer(TIMEOUT, on_timeout, (subp1, status_dict))
          timer.start()
#          time.sleep(TIMEOUT)
          subp1.wait()
          print(status_dict)
          open("logfile","w").close()
          os.system("mv logfile logfile"+str(nois)+".out")
     #     atexit.register(exit_handler, subp1.pid)
          #os.system("kill -9 {}".format(subp1.pid))
          time.sleep(2)

          _pass=0;_total=0;_per=1;
          #with open("nohup.out", "r") as fp:
          with io.open("logfile"+str(nois)+".out", "r", encoding="utf-8",errors="surrogateescape") as fp:
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

          print("PER="+str(_pass)+'/'+str(_total))
          if _total!=0:
            _per = (_total-_pass)/_total
            print('='+str(_per))
          PERS.append(_per)

  print(NOISES)
  print(PERS)

open(os.devnull, "w").close()
