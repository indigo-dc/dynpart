#!/usr/bin/env python

import os
import sys
import time
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
create and starts a new instance named vwn-<ip_seperated_with_dash>
Usage: new_instance.py

"""

"""
Algorithm logic

Assume: Image, flavor and keypair is defined in the conf file
Take: The authentication parameters from the conf file
Does: Creates and starts a new instance named vwn-<ip_seperated_with_dash>
In case of Error state it tries for max_tries before releasing the IP

"""


class NewInstance(Instance):

    def __init__(self, conf_file):
        Instance.__init__(self, conf_file)


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    n = NewInstance(conf_file)

    ext_net, = [x for x in n.neutron.list_networks()['networks'] if x[
        'router:external']]
    args = dict(floating_network_id=ext_net['id'])
    try:
        ip_obj = n.neutron.create_floatingip(body={'floatingip': args})
        ip = ip_obj['floatingip']['floating_ip_address']
    except Exception, e:
        mlog(n.logf, str(e))
        sys.exit(0)

    instance_name = "vwn-" + ip.replace('.', '-')
    success = False
    try_number = 0
    """create the instance"""
    while success is False and try_number < n.max_retries:
        try:
            instance = n.nova.servers.create(name=instance_name,
                                             image=n.image_id,
                                             flavor=n.flavor_id,
                                             nics=[
                                                 {'net-id': n.network_pri_id}],
                                             key_name=n.keyname)
            success = True
        except Exception, e:
            mlog(n.logf, str(e))
            success = False
            if not success:
                mlog(n.logf, "exiting in %d seconds" % n.sleeptime)
                time.sleep(n.sleeptime)
                sys.exit(0)

        mlog(n.logf, "Creating server: " + instance_name)
        mlog(n.logf, "Flavor: " + n.flavor)
        mlog(n.logf, "Image: " + n.image)
        mlog(n.logf, "Keypair name: " + n.keyname)

        status = instance.status

        """check the status of newly created instance
        until status changes from 'BUILD' to 'ACTIVE'"""
        while status == 'BUILD':
            time.sleep(n.sleeptime)
            instance = n.nova.servers.get(instance.id)
            status = instance.status
            mlog(n.logf, "status: %s" % status)

        if status == 'ACTIVE':
            success = True
            instance.add_floating_ip(ip)
            mlog(n.logf, "DONE")
        elif status == 'ERROR':
            success = False
            try_number = try_number + 1
            mlog(n.logf, "Error creating instance-try : %d" % try_number)
            mlog(n.logf, "Deleting the instance: " + instance_name)
            n.nova.servers.delete(instance.id)

        while try_number >= n.max_retries:
            mlog(n.logf, "Releasing the IP %s" % ip)
            ip_id = ip_obj['floatingip']['id']
            n.neutron.delete_floatingip(ip_id)
            sys.exit(0)

if __name__ == "__main__":
    main()
