#!/usr/bin/env python
"""
stop and delete an instance
Usage: Usage: delete_instance.py <name-of-the-instance>

"""


"""
Algorithm

Take: The authentication parameters from the conf file and name of the instance from cmdline
Does: Stops, deletes the instance and releases the IP

"""

import os
import sys
import time
import json
from novaclient.v2 import client
from neutronclient.v2_0 import client as neutronClient


def now():
    """returns human readable date and time"""
    return time.ctime(time.time())


def mlog(f, m, dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    script_name = os.path.basename(sys.argv[0])
    msg = "%s %s:" % (now(), script_name) + m
    f.write(msg + '\n')
    f.flush()
    if dbg:
        print msg


def help():
    print """"usage: delete_instance.py <name-of-the-instance> \n                                                                                               
Stops, deletes the instance and releases the IP
"""

conf_file = '/etc/indigo/dynpart/dynp.conf'

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
USERNAME = jc['USERNAME_d']
PASSWORD = jc['PASSWORD_d']
PROJECT_ID = jc['PROJECT_ID_d']
AUTH_URL = jc['AUTH_URL']
sleeptime = jc['sleeptime']
log_dir = jc['log_dir']
log_file = os.path.join(log_dir, jc['log_file'])

if not os.path.isdir(log_dir):
    print "%s log directory not found" % log_dir
    sys.exit(1)

logf = open(log_file, 'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
neutron = neutronClient.Client(
    username=USERNAME, password=PASSWORD, tenant_name=PROJECT_ID, auth_url=AUTH_URL)

try:
    instance_name = sys.argv[1]
except IndexError:
    help()
    sys.exit(1)

"""delete the instance"""
instance_id = [x.id for x in nova.servers.list() if x.name == instance_name]
try:
    nova.servers.delete(instance_id[0])
    mlog(logf, "Deleting the instance: " + instance_name)
except Exception, e:
    mlog(logf, "No server named %s found: %s" % (instance_name, str(e)))
    sys.exit(0)
ip = instance_name.partition('-')[2].replace('-', '.')
try:
    ip_obj = neutron.list_floatingips(floating_ip_address=ip)
    ip_id = ip_obj['floatingips'][0]['id']
    neutron.delete_floatingip(ip_id)
    mlog(logf, "Releasing the IP %s" % ip)
except Exception, e:
    mlog(logf, "No IP named %s found: %s" % (ip, str(e)))
