#!/usr/bin/env python

import os
import sys
import time
import random
from dynp_common import mlog
from instance import Instance

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
creates and starts many instances named vwn-<ip_seperated_with_dash>
in a loop with random (in order of 1 min) sleep time
Usage: create_instances.py

"""


"""
Algorithm

Assume: Image, flavor and keypair is defined in the conf file
Take: The authentication parameters from the conf file
Does:  Creates and starts many instance named vwn-<ip_seperated_with_dash>
In case of Error state it tries for max_tries before releasing the IP
"""


class CreateInstances(Instance):

    def __init__(self, conf_file):
        Instance.__init__(self, conf_file)
        self.tenant_id = self.nova.client.tenant_id
        self.instance_quota = self.nova.quotas.get(self.tenant_id).instances
        self.floatingip_quota = self.nova.quotas.get(
            self.tenant_id).floating_ips

    def get_floating_ip_usage(self):
        self.floating_ip_usage = len(self.nova.floating_ips.list())
        return self.floating_ip_usage

    def get_instance_usage(self):
        self.instance_usage = len(self.nova.servers.list())
        return self.instance_usage


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    c = CreateInstances(conf_file)

    ext_net, = [x for x in c.neutron.list_networks()['networks'] if x[
        'router:external']]
    args = dict(floating_network_id=ext_net['id'])

    got_ip = False
    while True:
        floating_ip_usage = c.get_floating_ip_usage()
        instance_usage = c.get_instance_usage()
        if instance_usage >= c.instance_quota:
            mlog(c.logf, "Instance quota exceeded..I'm sleeping")
            time.sleep(c.sleeptime)
            continue
        else:
            if floating_ip_usage >= c.floatingip_quota:
                mlog(c.logf, "No available IP-Try to release IP...Sleeping")
                time.sleep(c.sleeptime)
                continue
            elif not got_ip:
                ip_obj = c.neutron.create_floatingip(body={'floatingip': args})
                ip = ip_obj['floatingip']['floating_ip_address']
                ip_id = ip_obj['floatingip']['id']
                floating_ip_usage = c.get_floating_ip_usage()
                got_ip = True
            instance_name = "vwn-" + ip.replace('.', '-')
            try_number = 0
            sleep_big = c.sleeptime + random.random() * 60
            while try_number < c.max_retries:
                try:
                    instance = c.nova.servers.create(name=instance_name,
                                                     image=c.image_id,
                                                     flavor=c.flavor_id,
                                                     nics=[{'net-id':
                                                            c.network_pri_id}],
                                                     key_name=c.keyname)
                    instance_usage = c.get_instance_usage()
                except Exception, e:
                    mlog(c.logf, str(e))
                    continue
                mlog(c.logf, "Creating server: " + instance_name)
                mlog(c.logf, "Flavor: " + c.flavor)
                mlog(c.logf, "Image: " + c.image)
                mlog(c.logf, "Keypair name: " + c.keyname)
                """check the status of newly created instance
                until status changes from 'BUILD' to 'ACTIVE'"""
                status = instance.status
                while status == 'BUILD':
                    time.sleep(c.sleeptime)
                    instance = c.nova.servers.get(instance.id)
                    status = instance.status
                    mlog(c.logf, "status: %s" % status)
                if status == 'ACTIVE':
                    instance.add_floating_ip(ip)
                    mlog(c.logf, "DONE")
                    got_ip = False
                    break
                elif status == 'ERROR':
                    try_number = try_number + 1
                    mlog(c.logf, "Error creating instance-try:%d" % try_number)
                    c.nova.servers.delete(instance.id)
                    mlog(c.logf, "Deleting the instance: " + instance_name)
                    time.sleep(c.sleeptime)
                if try_number >= c.max_retries:
                    try:
                        mlog(c.logf, "Releasing the IP %s" % ip)
                        c.neutron.delete_floatingip(ip_id)
                        got_ip = False
                        continue
                    except Exception, e:
                        mlog(c.logf, str(e))
            mlog(c.logf, "Sleeping for %d seconds" % sleep_big)
            time.sleep(sleep_big)

if __name__ == "__main__":
    main()
