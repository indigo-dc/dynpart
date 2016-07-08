#!/usr/bin/env python

import os
import sys
import time
import random
import json
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient

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
    print """"usage: create_instances.py \n
Creates and starts many instance named vwn-<ip_seperated_with_dash>
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
    print "%s log Directory not found" % log_dir
    sys.exit(1)

logf = open(log_file, 'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
neutron = neutronClient.Client(username=USERNAME,
                               password=PASSWORD,
                               tenant_name=PROJECT_ID,
                               auth_url=AUTH_URL)

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

tenant_id = nova.client.tenant_id
instance_quota = nova.quotas.get(tenant_id).instances
floatingip_quota = nova.quotas.get(tenant_id).floating_ips
floating_ip_usage = len(nova.floating_ips.list())
instance_usage = len(nova.servers.list())

ext_net, = [x for x in neutron.list_networks()['networks'] if x[
    'router:external']]
args = dict(floating_network_id=ext_net['id'])

got_ip = False
while True:
    if instance_usage >= instance_quota:
        mlog(logf, "Instance quota exceeded..I'm sleeping")
        time.sleep(sleeptime)
        continue
    else:
        if floating_ip_usage >= floatingip_quota:
            mlog(logf, "No available IP-Try to release Floating IP...Sleeping")
            time.sleep(sleeptime)
            continue
        elif not got_ip:
            ip_obj = neutron.create_floatingip(body={'floatingip': args})
            ip = ip_obj['floatingip']['floating_ip_address']
            ip_id = ip_obj['floatingip']['id']
            floating_ip_usage = len(nova.floating_ips.list())
            got_ip = True
        instance_name = "vwn-" + ip.replace('.', '-')
        try_number = 0
        sleep_big = sleeptime + random.random() * 60
        while try_number < max_retries:
            try:
                instance = nova.servers.create(name=instance_name,
                                               image=image_id,
                                               flavor=flavor_id,
                                               nics=[
                                                   {'net-id': network_pri_id}],
                                               key_name=keyname)
                instance_usage = len(nova.servers.list())
            except Exception, e:
                mlog(logf, str(e))
                continue
            mlog(logf, "Creating server: " + instance_name)
            mlog(logf, "Flavor: " + flavor)
            mlog(logf, "Image: " + image_to_use)
            mlog(logf, "Keypair name: " + keyname)
            """check the status of newly created instance
            until status changes from 'BUILD' to 'ACTIVE'"""
            status = instance.status
            while status == 'BUILD':
                time.sleep(sleeptime)
                instance = nova.servers.get(instance.id)
                status = instance.status
                mlog(logf, "status: %s" % status)
            if status == 'ACTIVE':
                instance.add_floating_ip(ip)
                mlog(logf, "DONE")
                got_ip = False
                break
            elif status == 'ERROR':
                try_number = try_number + 1
                mlog(logf, "Error creating instance-try : %d" % try_number)
                nova.servers.delete(instance.id)
                mlog(logf, "Deleting the instance: " + instance_name)
                time.sleep(sleeptime)
            if try_number >= max_retries:
                try:
                    mlog(logf, "Releasing the IP %s" % ip)
                    neutron.delete_floatingip(ip_id)
                    got_ip = False
                    continue
                except Exception, e:
                    mlog(logf, str(e))
        mlog(logf, "Sleeping for %d seconds" % sleep_big)
        time.sleep(sleep_big)
