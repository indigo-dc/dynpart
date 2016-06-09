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

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    script_name =  os.path.basename(sys.argv[0])
    if dbg:
        f.write("%s %s:"%(now(), script_name)+m+'\n')
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

try:
    instance_name = sys.argv[1]
except IndexError:
    print "Usage: delete_instance.py <name-of-the-instance>"
    sys.exit(1)

"""delete the instance"""
mlog(logf, "Deleting the instance: "+instance_name)
ip = instance_name.partition('-')[2].replace('-','.')
ip_id = nova.floating_ips.find(ip=ip).id
mlog(logf, "Releasing the IP %s" %ip)
instance_id = [x.id for x in nova.servers.list() if x.name==instance_name]
nova.servers.delete(instance_id[0])
nova.floating_ips.delete(ip_id)
