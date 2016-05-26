#!/usr/bin/env python
"""
CLOUD stop and delete an instance script
Usage: Usage: delete_instance.py <name-of-the-instance>

"""


"""
Algorithm logic

Take: The authentication parameters from the conf file and name of the instance from cmdline.
Action: Stops and deletes the instance

"""
import os,sys,time
import json
from novaclient.v2 import client

##TODO : sys.path.add('my_fancy_dir')
##from dynp_common import now,mlog

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    if dbg:
        f.write("%s: "%now()+m+'\n')
        f.flush()

conf_dir = "/etc/indigo/dynp"
conf_file = 'dynp.conf' 

jcf = os.path.join(conf_dir,conf_file)
if not os.path.isfile(jcf):
        print "%s file not found"%jcf
        sys.exit(1)
        

try:
    jc = json.load(open(jcf,'r'))
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
log_dir = jc['log_dir']
log_file = jc['log_file']
sleeptime = jc['sleeptime']

log_fn = os.path.join(log_dir,log_file)
if not os.path.isfile(log_fn):
        print "%s file not found"%log_fn
        sys.exit(1)

logf = open(log_fn,'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

try:
    instance_name = sys.argv[1]
except IndexError:
    print "Usage: delete_instance.py <name-of-the-instance>"
    sys.exit(1)

"""delete the instance"""
mlog(logf, "Deleting the instance: "+instance_name)
instance_id = [x.id for x in nova.servers.list() if x.name==instance_name]
nova.servers.delete(instance_id[0])
