#!/usr/bin/env python

import os
import sys
import time
import json
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient

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

conf_file = '/etc/indigo/dynpart/dynp.conf'


def now():
    """returns human readable date and time"""
    return time.ctime(time.time())


def mlog(f, m, dbg=True):
    """mlog(<file>,log message[,dbg=True]) ->
    append one log line to <file> if dbg == True"""
    script_name = os.path.basename(sys.argv[0])
    msg = "%s %s:" % (now(), script_name) + m
    f.write(msg + '\n')
    f.flush()
    if dbg:
        print msg


def help():
    print """"usage: new_instance.py \n
Creates and starts a new instance named vwn-<ip_seperated_with_dash>
In case of Error state it tries for max_tries before releasing the IP
"""

if not os.path.isfile(conf_file):
    print "%s file not found" % conf_file
    sys.exit(1)

try:
    jc = json.load(open(conf_file, 'r'))
except ValueError:
    print "error while reading %s" % conf_file
except AttributeError:
    print "wrong json syntax : check your syntax in %s" % conf_file
except Exception, e:
    print str(e)
    sys.exit(0)

"""Initialization from Conf file"""
USERNAME = jc['auth']['USERNAME_d']
PASSWORD = jc['auth']['PASSWORD_d']
PROJECT_ID = jc['auth']['PROJECT_ID_d']
AUTH_URL = jc['auth']['AUTH_URL']

log_dir = jc['logging']['log_dir']
log_file = os.path.join(log_dir, jc['logging']['log_file'])

if not os.path.isdir(log_dir):
    print "%s log directory not found" % log_dir
    sys.exit(1)

logf = open(log_file, 'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
neutron = neutronClient.Client(username=USERNAME,
                               password=PASSWORD,
                               tenant_name=PROJECT_ID,
                               auth_url=AUTH_URL)

ext_net, = [x for x in neutron.list_networks()['networks'] if x[
    'router:external']]
args = dict(floating_network_id=ext_net['id'])
try:
    ip_obj = neutron.create_floatingip(body={'floatingip': args})
    ip = ip_obj['floatingip']['floating_ip_address']
except Exception, e:
    # TODO: consider logging
    mlog(logf, str(e))
    sys.exit(0)

instance_name = "vwn-" + ip.replace('.', '-')

image_to_use = jc['VM_conf']['image']
image_id = nova.images.find(name=image_to_use).id

flavor = jc['VM_conf']['flavor']
flavor_id = nova.flavors.find(name=flavor).id

network_pri_id = nova.networks.find(label='private').id

keyname = jc['VM_conf']['keyname']
conf_dir = os.path.dirname(conf_file)

if not nova.keypairs.findall(name=keyname):
    with open(os.path.join(conf_dir, keyname + ".pub")) as fpubkey:
        nova.keypairs.create(name=keyname, public_key=fpubkey.read())

max_retries = jc['VM_conf']['max_retries']
sleeptime = jc['VM_conf']['sleeptime']
success = False
try_number = 0
"""create the instance"""
while success is False and try_number < max_retries:
    try:
        instance = nova.servers.create(name=instance_name,
                                       image=image_id,
                                       flavor=flavor_id,
                                       nics=[{'net-id': network_pri_id}],
                                       key_name=keyname)
        success = True
    except Exception, e:
        mlog(logf, str(e))
        success = False
        if not success:
            mlog(logf, "exiting in %d seconds" % sleeptime)
            time.sleep(sleeptime)
            sys.exit(0)

    mlog(logf, "Creating server: " + instance_name)
    mlog(logf, "Flavor: " + flavor)
    mlog(logf, "Image: " + image_to_use)
    mlog(logf, "Keypair name: " + keyname)

    status = instance.status

    """check the status of newly created instance
    until status changes from 'BUILD' to 'ACTIVE'"""
    while status == 'BUILD':
        time.sleep(sleeptime)
        instance = nova.servers.get(instance.id)
        status = instance.status
        mlog(logf, "status: %s" % status)

    if status == 'ACTIVE':
        success = True
        instance.add_floating_ip(ip)
        mlog(logf, "DONE")
    elif status == 'ERROR':
        success = False
        try_number = try_number + 1
        mlog(logf, "Error creating instance-try : %d" % try_number)
        mlog(logf, "Deleting the instance: " + instance_name)
        nova.servers.delete(instance.id)

    while try_number >= max_retries:
        mlog(logf, "Releasing the IP %s" % ip)
        ip_id = ip_obj['floatingip']['id']
        neutron.delete_floatingip(ip_id)
        sys.exit(0)
