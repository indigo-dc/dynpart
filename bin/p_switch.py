#!/usr/bin/env python

import os
import sys
import commands
from novaclient import client
from dynp_common import mlog, get_jsondict, put_jsondict, get_value

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

"""
Makes the initial preperation of json dictionary and switch/moves the nodes
 to a particular set depending on the request i.e FROM/TO batch/cloud

Usage: p_switch.py to_batch|to_cloud filename

"""

"""
Algorithm

Assume: Status of nodes is defined in a given json file and
list of nodes to switch is provided in a file via commandline

Take: Json dictionary from json file and list of nodes to switch
from file via commandline

Does: Makes the initial preperation of json dictionary and switch/moves
the nodes to a particular set depending on the request i.e FROM/TO batch/cloud
"""


def help():
    print """"usage: p_switch.py to_batch|to_cloud filename\n
    Makes the initial preperation of json dictionary and switch/moves the nodes
    to a particular set depending on the request i.e FROM/TO batch/cloud
"""


class Switch(object):
    """Switch class for switch / move of nodes to a particular set
    depending on the request i.e FROM / TO batch / cloud for all modules"""

    def __init__(self, conf_file, opt, listfile):
        self.conf_file = conf_file
        self.opt = opt
        self.listfile = listfile
        self.jc = get_jsondict(self.conf_file)

        lgdict = get_value(self.jc, 'logging')
        log_dir = get_value(lgdict, 'log_dir')
        if not os.path.isdir(log_dir):
            print "Please check the %s directory" % log_dir
            sys.exit(1)
        log_filename = get_value(lgdict, 'log_file')
        self.log_file = os.path.join(log_dir, log_filename)
        self.logf = open(self.log_file, 'a')

        switch_dict = get_value(self.jc, 'switch')
        self.farm_json_file = get_value(switch_dict, 'batch_cloud_json')
        self.farm_json_dict = get_jsondict(self.farm_json_file)

        authdict = get_value(self.jc, 'auth')
        self.USERNAME = get_value(authdict, 'USERNAME')
        self.PASSWORD = get_value(authdict, 'PASSWORD')
        self.PROJECT_ID = get_value(authdict, 'PROJECT_ID')
        self.AUTH_URL = get_value(authdict, 'AUTH_URL')
        self.VERSION = get_value(authdict, 'VERSION')

        self.nova = client.Client(self.VERSION,
                                  self.USERNAME,
                                  self.PASSWORD,
                                  self.PROJECT_ID,
                                  self.AUTH_URL)

        try:
            self.host_list = [x for x in open(
                self.listfile, 'r').read().split() if x]
        except:
            mlog(self.logf, "Error while parsing %s" % self.listfile)
            self.host_list = []

        self.valid_host_list = []
        self.cn_list = []

    def get_cn_list(self):
        for x in self.nova.hypervisors.list():
            self.cn_list.append(x.hypervisor_hostname)
        return self.cn_list

    def check_valid_b_host(self, hostN):
        cmd = """bhosts %s """ % hostN
        e, o = commands.getstatusoutput(cmd)
        if e:
            mlog(self.logf, "Failed with %s" % o)
            return False
        return True

    def get_valid_b_list(self):
        self.valid_b_list = []
        for hostN in self.host_list:
            if self.check_valid_b_host(hostN):
                self.valid_b_list.append(hostN)
            else:
                pass
        return self.valid_b_list

    def get_valid_cn_list(self):
        self.valid_cn_list = []
        for hostN in self.host_list:
            if hostN in self.cn_list:
                self.valid_cn_list.append(hostN)
        return self.valid_cn_list

    def pre_switch_action(self, X, Y, valid_host_list):
        """Creats the set Z from the valid nodes in the listfile"""
        self.valid_host_list = valid_host_list
        Z = set(self.valid_host_list)
        """Firstly X should not include the nodes which are already in
        list Y and Secondly it should contain unique elements from
        present and past requests"""
        already_in_Y = Z & set(self.farm_json_dict[Y])
        already_in_X = Z & set(self.farm_json_dict[X])
        for node in already_in_Y:
            mlog(self.logf, "Node %s is already in %s - Doing Nothing"
                 % (node, Y))
        for node in already_in_X:
            mlog(self.logf, "Node %s is already in %s - Doing Nothing"
                 % (node, X))
        Z = Z - set(self.farm_json_dict[Y])
        add_to_X = Z - set(self.farm_json_dict[X])
        for host in add_to_X:
            mlog(self.logf, "Moving node %s to %s" % (host, X))
        self.farm_json_dict[X] = list(set(self.farm_json_dict[X]) | Z)
        for hostname in self.farm_json_dict[X]:
            mlog(self.logf, "Node %s will be moved to %s" % (hostname, Y))
        return self.farm_json_dict


def main():
    if len(sys.argv) <= 2:
        help()
        sys.exit(0)

    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    opt = sys.argv[1]
    match = (opt in ['to_cloud', 'to_batch'])
    if not match:
        print "Option doesn't match, options are : to_cloud or to_batch"
        sys.exit(0)

    listfile = sys.argv[2]
    if not os.path.isfile(listfile):
        print "Please check the path of the listfile"
        sys.exit(1)

    sw = Switch(conf_file, opt, listfile)
    sw.get_cn_list()

    if sw.opt == 'to_cloud':
        valid_host_list = sw.get_valid_cn_list()
        sw.farm_json_dict = sw.pre_switch_action('B2CR', 'C', valid_host_list)
    elif sw.opt == 'to_batch':
        valid_host_list = sw.get_valid_b_list()
        sw.farm_json_dict = sw.pre_switch_action('C2BR', 'B', valid_host_list)

    put_jsondict(sw.farm_json_file, sw.farm_json_dict)

if __name__ == "__main__":
    main()
