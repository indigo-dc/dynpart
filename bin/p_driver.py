#!/usr/bin/env python

import os
import sys
import time
import json
import commands
from neutronclient.v2_0 import client as neutronClient
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
Partition director : Manages the switching of role and
status of nodes from/to Batch/Cloud

Usage: p_driver.py

"""

"""
Algorithm

Assume: Status of nodes is defined in a given json file
Take: Json dictionary from json file
Does: Manages the switching of role and status of nodes from/to Batch/Cloud
"""


class Driver(object):

    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.exe_time = time.time()
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
        self.ttl_period = int(get_value(switch_dict, 'ttl_period'))
        self.bjobs_r = get_value(switch_dict, 'bjobs_r')
        self.rj_file = get_value(switch_dict, 'rj_file')

        mjf_dict = get_value(self.jc, 'machine_job_feature')
        self.mjf_dir = get_value(mjf_dict, 'TTL_filepath')
        if not os.path.isdir(self.mjf_dir):
            os.mkdir(self.mjf_dir)

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
        self.neutron = neutronClient.Client(username=self.USERNAME,
                                            password=self.PASSWORD,
                                            tenant_name=self.PROJECT_ID,
                                            auth_url=self.AUTH_URL)

    def isError(self):
        with open(self.rj_file, 'r') as f:
            s = f.read()
            return s.startswith('Error')

    def count_N_jobs(self, hostN):
        """count_N_vm(<host>) -> Returns the number of
        running batch jobs on <host>"""
        hostname = hostN.partition('.')[0]
        HRJ = [x[:4] for x in self.RJ if x[2].find(hostname) >= 0]
        count = len(HRJ)
        return count

    def make_switch(self, hostN, X, Y):
        """make_switch(<host>,list X,list Y) ->
        Switch the <host> from list X to list Y i.e append <host> to list X and
        removes the same from list Y and returns the updated lists """
        self.farm_json_dict[X].append(hostN)
        while hostN in self.farm_json_dict[Y]:
            self.farm_json_dict[Y].remove(hostN)

    def enable_nova(self, hostN):
        """enable_nova(<host>) -> Enables nova service on <host> """
        try:
            self.nova.services.enable(host=hostN, binary="nova-compute")
            mlog(self.logf, "Enabled nova service on %s" % hostN)
            return True
        except Exception, e:
            mlog(self.logf, str(e))
            return False
            sys.exit(1)

    def count_N_vm(self, hostN):
        """count_N_vm(<host>) -> Returns the number of running VMs on <host>"""
        for x in self.nova.hypervisors.list():
            if (x.hypervisor_hostname == hostN):
                return x.running_vms

    def stop_running_vm(self, hostN):
        """stop_running_vm(<host>) -> Stop all the running VMs on <host> """
        try:
            list_server = [x for x in self.nova.servers.list(
                search_opts={'host': hostN, 'all_tenants': 1})]
        except Exception, e:
            mlog(self.logf, str(e))
        for server in list_server:
            try:
                self.nova.servers.delete(server.id)
            except Exception, e:
                mlog(self.logf, str(e))
            name = server.name
            ip = name.partition('-')[2].replace('-', '.')
            try:
                ip_obj = self.neutron.list_floatingips(floating_ip_address=ip)
            except Exception, e:
                mlog(self.logf, str(e))
            ip_id = ip_obj['floatingips'][0]['id']
            try:
                self.neutron.delete_floatingip(ip_id)
            except Exception, e:
                mlog(self.logf, str(e))
            mlog(self.logf, "Releasing the IP %s" % ip)
        mlog(self.logf, "Stopped and deleted all the VM on %s" % hostN)
        return True

    def check_c2b(self):
        """check_c2b(<dict>) -> Checks each host in C2B if it is ready for
        switch and makes the switch when either host has #VM's = 0 or time
        now > TTL, Returns the updated <dict>"""
        c2b_copy = self.farm_json_dict['C2B'][:]
        for hostN in c2b_copy:
            shutdown_file = hostN.replace('.', '-') + '_ttl'
            sdf = os.path.join(self.mjf_dir, shutdown_file)
            if self.exe_time <= self.farm_json_dict['C2B_TTL'][hostN]:
                count = self.count_N_vm(hostN)
                if count == 0:
                    mlog(self.logf, "No of running VM on %s is %d" %
                         (hostN, count))
                    mlog(self.logf, "Moving %s from list C2B to B" % hostN)
                    self.make_switch(hostN, 'B', 'C2B')
                    del self.farm_json_dict['C2B_TTL'][hostN]
                    os.remove(sdf)
            else:
                mlog(self.logf, "TTL has expired since %d > %d" %
                     (self.exe_time, self.farm_json_dict['C2B_TTL'][hostN]))
                self.stop_running_vm(hostN)
                mlog(self.logf, "Moving %s from list C2B to B" % hostN)
                self.make_switch(hostN, 'B', 'C2B')
                del self.farm_json_dict['C2B_TTL'][hostN]
                os.remove(sdf)
        return self.farm_json_dict

    def check_b2c(self):
        """check_b2c(<dict>) -> Checks each host in B2C if it is ready for
        switch and makes the switch when host has #Running_jobs = 0,
        Returns the updated <dict>"""
        cmd = """python %s > %s""" % (self.bjobs_r, self.rj_file)
        e, o = commands.getstatusoutput(cmd)
        if e:
            mlog(self.logf, "./bjobs_r Failed!")

        if not self.isError():
            self.RJ = [x.rstrip().split(None, 4)
                       for x in open(self.rj_file, 'r').readlines()]
            b2c_copy = self.farm_json_dict['B2C'][:]
            for hostN in b2c_copy:
                count = self.count_N_jobs(hostN)
                if count == 0:
                    mlog(self.logf, "No of jobs running on %s is %d" %
                         (hostN, count))
                    mlog(self.logf, "Moving %s from list B2C to C" % hostN)
                    self.make_switch(hostN, 'C', 'B2C')
                    self.enable_nova(hostN)
                else:
                    mlog(self.logf, "No of jobs running on %s is %d" %
                         (hostN, count))
                    mlog(self.logf, "Not moving %s to list C" % hostN)

        return self.farm_json_dict

    def disable_nova(self, hostN):
        """disable_nova(<host>) -> Disables nova service on <host> """
        try:
            self.nova.services.disable_log_reason(
                host=hostN, binary="nova-compute", reason='test')
            mlog(self.logf, "Disabled nova service on %s" % hostN)
            return True
        except Exception, e:
            mlog(self.logf, str(e))
            return False
            sys.exit(1)


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    d = Driver(conf_file)

    ttl = int(d.exe_time + d.ttl_period)

    d.farm_json_dict['C2B'] = list(
        set(d.farm_json_dict['C2BR']) | set(d.farm_json_dict['C2B']))
    # consider user quotas (upper limit of no. of hosts in user area)
    C2B = d.farm_json_dict['C2B']
    for hostN in C2B:
        d.disable_nova(hostN)
        if hostN not in d.farm_json_dict['C2B_TTL']:
            d.farm_json_dict['C2B_TTL'][hostN] = ttl
            mjf_file = hostN.replace('.', '-') + '_ttl'
            jff = os.path.join(d.mjf_dir, mjf_file)
            try:
                jf = open(jff, 'w')
                jf.write("%s" % ttl + '\n')
                jf.flush()
            except Exception, e:
                mlog(d.logf, str(e))
    d.farm_json_dict['C'] = list(
        set(d.farm_json_dict['C']) - set(d.farm_json_dict['C2B']))
    d.farm_json_dict['C2BR'] = []

    d.farm_json_dict['B2C'] = list(
        set(d.farm_json_dict['B2CR']) | set(d.farm_json_dict['B2C']))
    d.farm_json_dict['B'] = list(
        set(d.farm_json_dict['B']) - set(d.farm_json_dict['B2C']))
    d.farm_json_dict['B2CR'] = []

    d.farm_json_dict = d.check_c2b()
    d.farm_json_dict = d.check_b2c()

    put_jsondict(d.farm_json_file, d.farm_json_dict)

if __name__ == "__main__":
    main()
