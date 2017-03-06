#!/usr/bin/env python

import os
import sys
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient
from dynp_common import mlog, get_jsondict, get_value

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
stop and delete an instance
Usage: Usage: delete_instance.py <name-of-the-instance>

"""


"""
Algorithm

Take: The authentication parameters from the conf file
and name of the instance from cmdline
Does: Stops, deletes the instance and releases the IP

"""


def help():
    print """"usage: delete_instance.py <name-of-the-instance> \n
    Stops, deletes the instance and releases the IP
"""


class DeleteInstance(object):

    def __init__(self, conf_file):
        self.conf_file = conf_file
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
        self.USERNAME = get_value(authdict, 'USERNAME_d')
        self.PASSWORD = get_value(authdict, 'PASSWORD_d')
        self.PROJECT_ID = get_value(authdict, 'PROJECT_ID_d')
        self.AUTH_URL = get_value(authdict, 'AUTH_URL')

        self.nova = client.Client(
            self.USERNAME, self.PASSWORD, self.PROJECT_ID, self.AUTH_URL)
        self.neutron = neutronClient.Client(username=self.USERNAME,
                                            password=self.PASSWORD,
                                            tenant_name=self.PROJECT_ID,
                                            auth_url=self.AUTH_URL)


def main():
    conf_file = '/etc/indigo/dynpart/dynp.conf'
    if not os.path.isfile(conf_file):
        print "%s file not found" % conf_file
        sys.exit(1)

    d = DeleteInstance(conf_file)

    try:
        instance_name = sys.argv[1]
    except IndexError:
        help()
        sys.exit(1)

    """delete the instance"""
    instance_id = [x.id for x in d.nova.servers.list() if x.name ==
                   instance_name]
    try:
        d.nova.servers.delete(instance_id[0])
        mlog(d.logf, "Deleting the instance: " + instance_name)
    except Exception, e:
        mlog(d.logf, "No server named %s found: %s" % (instance_name, str(e)))
        sys.exit(0)

    ip = instance_name.partition('-')[2].replace('-', '.')
    try:
        ip_obj = d.neutron.list_floatingips(floating_ip_address=ip)
        ip_id = ip_obj['floatingips'][0]['id']
        d.neutron.delete_floatingip(ip_id)
        mlog(d.logf, "Releasing the IP %s" % ip)
    except Exception, e:
        mlog(d.logf, "No IP named %s found: %s" % (ip, str(e)))

if __name__ == "__main__":
    main()
