#!/usr/bin/env python
import os
import sys
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient
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


class Instance(object):

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
        vm_conf_dict = get_value(self.jc, 'VM_conf')
        self.image = get_value(vm_conf_dict, 'image')
        self.flavor = get_value(vm_conf_dict, 'flavor')
        self.keyname = get_value(vm_conf_dict, 'keyname')
        self.max_retries = get_value(vm_conf_dict, 'max_retries')
        self.sleeptime = get_value(vm_conf_dict, 'sleeptime')

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

        self.image_id = self.nova.images.find(name=self.image).id
        self.flavor_id = self.nova.flavors.find(name=self.flavor).id
        self.network_pri_id = self.nova.networks.find(label='private').id
        if not self.nova.keypairs.findall(name=self.keyname):
            mlog(self.logf,  "Please associate your own keypair..Exiting ")
            sys.exit(0)

# def main():
#     conf_file = '/etc/indigo/dynpart/dynp.conf'
#     if not os.path.isfile(conf_file):
#         print "%s file not found" % conf_file
#         sys.exit(1)

#     n = Instance(conf_file)
#     attrs = vars(n)
#     print '\n '.join("%s: %s" % item for item in attrs.items())

# if __name__ == "__main__":
#     main()
