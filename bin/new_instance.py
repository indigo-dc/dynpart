#!/usr/bin/env python
"""
CLOUD create and start up a new instance script
Usage: new_instance.py <name-of-the-instance>

"""


"""
Algorithm logic

Assume: Image, flavor and keypair is defined in the conf file
Take: The authentication parameters from the conf file and name of the instance from cmdline
Action: Creates a new instance and checks the status of instance until it becomes ACTIVE

"""

import os,sys,time
import json
from novaclient.v2 import client

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    if dbg:
        f.write("%s: "%now()+m+'\n')
        f.flush()

homedir = '/home/TIER1/sdalpra/demo/'
conf_dir = os.path.join(homedir,"etc/")
conf_file = os.path.join(conf_dir,'dynp.conf')

if not os.path.isfile(conf_file):
        print "%s file not found"%conf_file
        sys.exit(1)

try:
    jc = json.load(open(conf_file,'r'))
except ValueError:
    print "error while reading %s"%conf_file
except AttributeError:
    print "wrong json syntax : check your syntax in %s" %conf_file
except Exception,e:
    print str(e)
    sys.exit(0)

"""Initialization from Conf file"""
USERNAME = jc['USERNAME_d']
PASSWORD = jc['PASSWORD_d']
PROJECT_ID = jc['PROJECT_ID_d']
AUTH_URL = jc['AUTH_URL']
log_dir = os.path.join(homedir,jc['log_dir'])
log_file = os.path.join(log_dir,jc['log_file'])
sleeptime = jc['sleeptime']

if not os.path.isdir(log_dir):
    print "%s log directory not found"%log_dir
    sys.exit(1)

logf = open(log_file,'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

floating_ip = nova.floating_ips.create()
instance_name = "vwn-"+floating_ip.ip.replace('.','-')

image_used = jc['image']
image_id = nova.images.find(name=image_used).id

flavor = jc['flavor']
flavor_id = nova.flavors.find(name=flavor).id

network_pri_id = nova.networks.find(label='private').id

keyname = jc['keyname']

if not nova.keypairs.findall(name=keyname):
    with open(os.path.join(conf_dir,keyname+".pub")) as fpubkey:
        nova.keypairs.create(name=keyname, public_key=fpubkey.read())

success = False
"""create the instance"""
try:
    instance = nova.servers.create(name=instance_name,
                                   image=image_id, 
                                   flavor=flavor_id,
                                   nics=[{'net-id': network_pri_id}],
                                   key_name=keyname)
    success = True
except Exception,e:
    mlog(logf, str(e))
    success = False
    if not success:
        mlog(logf, "exiting in 10 seconds")
        time.sleep(10)
        sys.exit(0)

mlog(logf, "Creating server: "+instance_name)
mlog(logf, "Flavor: "+flavor)
mlog(logf, "Image: "+image_used)
mlog(logf, "Keypair name: "+keyname)

status = instance.status

"""check the status of newly created instance, After sometime it changes status from 'BUILD' to 'ACTIVE'"""
while status == 'BUILD':
    time.sleep(sleeptime)
    instance = nova.servers.get(instance.id)
    status = instance.status
    mlog(logf, "status: %s" % status)
instance = nova.servers.find(name=instance_name)
instance.add_floating_ip(floating_ip)
mlog(logf, "DONE")
