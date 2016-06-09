#!/usr/bin/env python

#queste cose da mettere in file conf


cmd_sleep = 10
queue = 'short'

sub_cmd = 'bsub -q %s "/bin/sleep %%d"'%(queue)

max_pend = 300
min_pend = 50
avg_sleep = 280
nap = 5

import os,sys,time
import random
import commands

sleeptime = lambda : cmd_sleep + int(random.random() * avg_sleep)

def get_pend(queue):
    e,o = commands.getstatusoutput('bqueues %s'%queue)
    if e:
        return -1
    return int(o.split()[-2])

while True:
    np = get_pend(queue)
    print "pending jobs:",np
    if np < 5 :
        for n in range(max_pend):
            cmd = sub_cmd % sleeptime()
            print "Executing: %s"%cmd
            e,o = commands.getstatusoutput(cmd)
            if e:
                print "Error submitting job"
            time.sleep(1)
    time.sleep(nap)
