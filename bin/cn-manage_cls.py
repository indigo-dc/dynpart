#!/usr/bin/env python

import os
import sys
import time
import getopt
import commands
from novaclient.v2 import client
from dynp_common import mlog, get_jsondict, get_value

"""
Copyright (c) 2015 INFN - INDIGO-DataCloud
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
permissions and limitations under the License.
"""
"""
Manage nova compute service i.e enable/disable compute service on list of CN
Usage:
python cn-manage.py --mode=enable --file=listcn --reason="test" OR
python cn-manage.py -mode enable -f listcn -r "test"'''

"""

"""
Algorithm

Take: The authentication parameters from the conf file
and mode=enable|diable, list of CN's and reason from cmdline
Action: Enable|disable the nova compute service on list of
CN's for a defined reason
"""


def help():
    print """Usage: python cn-manage.py --mode=enable --file=listcn --reason="test" OR
    python cn-manage.py -m enable -f listcn -r "test"
    Enable|disable the nova compute service on list of
    CN's for a defined reason
"""


class CnManage(object):

    def __init__(self, conf_file, mode, listcn, reason):
        self.conf_file = conf_file
        self.mode = mode
        self.listcn = listcn
        self.reason = reason
        self.jc = get_jsondict(self.conf_file)
        lgdict = get_value(self.jc, 'logging')
        log_dir = get_value(lgdict, 'log_dir')
        if not os.path.isdir(log_dir):
            print "Please check the %s directory" % log_dir
            sys.exit(1)
        log_filename = get_value(lgdict, 'log_file')
        self.log_file = os.path.join(log_dir, log_filename)
        self.logf = open(self.log_file, 'a')

        authdict = get_value(self.jc, 'auth')
        self.USERNAME = get_value(authdict, 'USERNAME')
        self.PASSWORD = get_value(authdict, 'PASSWORD')
        self.PROJECT_ID = get_value(authdict, 'PROJECT_ID')
        self.AUTH_URL = get_value(authdict, 'AUTH_URL')

        self.nova = client.Client(
            self.USERNAME, self.PASSWORD, self.PROJECT_ID, self.AUTH_URL)

        try:
            self.host_list = [x for x in open(
                self.listcn, 'r').read().split() if x]
        except:
            mlog(self.logf, "Error while parsing %s" % self.listcn)
            self.host_list = []


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    if len(sys.argv) <= 6:
        help()
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:f:r:", [
                                   "mode=", "file=", "reason="])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-f", "--file"):
            listcn = arg
            if not os.path.isfile(listcn):
                print "Please check the path of the listcn"
                sys.exit(1)
        elif opt in ("-r", "--reason"):
            reason = arg

    match = (mode in ['enable', 'disable'])
    if not match:
        print "Option doesn't match, options are : enable or disable"
        sys.exit(0)

    c_manage = CnManage(conf_file, mode, listcn, reason)

    for cnname in c_manage.host_list:
        """Enabling/Disabling the compute service on host"""
        if (c_manage.mode == "enable"):
            try:
                c_manage.nova.services.enable(
                    host=cnname, binary="nova-compute")
                mlog(c_manage.logf, "Enabled the Compute Node " + cnname)
            except Exception, e:
                mlog(c_manage.logf, "No server named %s found: %s" %
                     (cnname, str(e)))
                sys.exit(0)
        elif (c_manage.mode == "disable"):
            try:
                c_manage.nova.services.disable_log_reason(
                    host=cnname, binary="nova-compute", reason=c_manage.reason)
                mlog(c_manage.logf, 'Disabled the Compute Node ' + cnname)
            except Exception, e:
                mlog(c_manage.logf, "No server named %s found: %s" %
                     (cnname, str(e)))
                sys.exit(0)

if __name__ == "__main__":
    main()
