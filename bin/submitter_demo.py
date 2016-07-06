#!/usr/bin/env python

import os
import sys
import time
import random
import commands
import json

# queste cose da mettere in file conf


conf_file = '/etc/indigo/dynpart/dynp.conf'

jconf = json.load(open(conf_file, 'r'))

jc = jconf["batch_submitter"]
cmd_sleep = jc['cmd_sleep']
queue = jc['queue']
max_pend = jc['max_pend']
min_pend = jc['min_pend']
avg_sleep = jc['avg_sleep']
nap = jc['nap']


def sleeptime(avg_nap=avg_sleep):
    return int(random.random() * avg_nap)


def get_pend(queue):
    e, o = commands.getstatusoutput('bqueues %s' % queue)
    if e:
        return -1
    return int(o.split()[-3])

json.load(open(conf_file, 'r'))

cmd = "bsub -q %s 'sleep %%d'" % (queue)

while True:
    np = get_pend(queue)
    print "pending jobs:", np
    if np < 5:
        for n in range(max_pend):
            sub_cmd = cmd % sleeptime(avg_sleep)
            print "Executing: %s" % sub_cmd
            e, o = commands.getstatusoutput(sub_cmd)
            if e:
                print "Error submitting job"
            time.sleep(1)
    time.sleep(nap)
