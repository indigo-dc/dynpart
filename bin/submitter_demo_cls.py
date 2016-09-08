#!/usr/bin/env python

import os
import sys
import time
import random
import commands
from dynp_common import get_jsondict, get_value

"""Copyright (c) 2015 INFN - INDIGO-DataCloud
All Rights Reserved
Licensed under the Apache License, Version 2.0;
you may not use this file except in compliance with the
License. You may obtain a copy of the License at:
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
See the License for the specific language governing
permissions and limitations under the License."""


class BatchJobSubmitter(object):

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.jc = get_jsondict(self.conf_file)
        self.batch_submitter_dict = get_value(self.jc, 'batch_submitter')
        self.cmd_sleep = get_value(self.batch_submitter_dict, 'cmd_sleep')
        self.queue = get_value(self.batch_submitter_dict, 'queue')
        self.max_pend = get_value(self.batch_submitter_dict, 'max_pend')
        self.avg_sleep = get_value(self.batch_submitter_dict, 'avg_sleep')
        self.nap = get_value(self.batch_submitter_dict, 'nap')

    def sleeptime(self):
        return int(random.random() * self.avg_sleep)

    def get_pend(self):
        e, o = commands.getstatusoutput('bqueues %s' % self.queue)
        if e:
            return -1
        return int(o.split()[-3])


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    bjs = BatchJobSubmitter(conf_file)
    cmd = "bsub -q %s 'sleep %%d'" % (bjs.queue)

    while True:
        np = bjs.get_pend()
        print "pending jobs:", np
        if np < 5:
            for n in range(bjs.max_pend):
                sub_cmd = cmd % bjs.sleeptime()
                print "Executing: %s" % sub_cmd
                e, o = commands.getstatusoutput(sub_cmd)
                if e:
                    print "Error submitting job"
                time.sleep(1)
        time.sleep(bjs.nap)

if __name__ == "__main__":
    main()
