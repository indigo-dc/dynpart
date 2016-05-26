#!/usr/bin/env python
"""
CLOUD Manage enable/disable of nova compute service on compute node script
Usage: Two formats
    python cn-manage.py --mode=enable --cnname=wn-206-01-01-02-b.cr.cnaf.infn.it --reason="test to enable"
    python cn-manage.py -mode enable -c wn-206-01-01-02-b.cr.cnaf.infn.it -r "test to enable"'''

"""


"""
Algorithm logic

Take: The authentication parameters from the conf file and Mode=enable/diable, Compute Node name and reason from cmdline.
Action: Enable/disable the nova compute service on compute node for a defined reason

"""

import os,sys,time,getopt
import json
from novaclient.v2 import client

##TODO : make stong and error free argument matching

mode = ''
cnname = ''
reason = ''

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    if dbg:
        f.write("%s: "%now()+m+'\n')
        f.flush()    
    
try:
    opts, args = getopt.getopt(sys.argv[1:],"hm:c:r:",["mode=","cnname=","reason="])
except getopt.GetoptError:
    print '''Usage: python cn-manage.py --mode=enable --cnname=wn-206-01-01-02-b.cr.cnaf.infn.it --reason="test to enable"
    python cn-manage.py -mode enable -c wn-206-01-01-02-b.cr.cnaf.infn.it -r "test to enable"'''
    sys.exit(2)
    
for opt, arg in opts:
    if opt == '-h':
        print '''Usage: python cn-manage.py --mode=enable --cnname=wn-206-01-01-02-b.cr.cnaf.infn.it --reason="test to enable"
        python cn-manage.py -mode enable -c wn-206-01-01-02-b.cr.cnaf.infn.it -r "test to enable"'''
        sys.exit()
    elif opt in ("-m","--mode"):
        mode = arg
    elif opt in ("-c","--cnname"):
        cnname = arg
    elif opt in ("-r","--reason"):
        reason = arg

conf_dir = "/home/CMS/sonia.taneja/demo/etc/"
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

"""Initialization from Conf file- Admin authentication"""
USERNAME = jc['USERNAME']
PASSWORD = jc['PASSWORD']
PROJECT_ID = jc['PROJECT_ID']
AUTH_URL = jc['AUTH_URL']
log_dir = jc['log_dir']
log_file = jc['log_file']
sleeptime = jc['sleeptime']

log_fn = os.path.join(log_dir,log_file)
if not os.path.isdir(log_dir):
        print "%s file not found"%log_dir
        sys.exit(1)

logf = open(log_fn,'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

"""Enabling/Disabling the compute service on host"""
if (mode == "enable"):
    nova.services.enable(host=cnname, binary="nova-compute")
    mlog(logf, "Enabled the Compute Node "+cnname)
elif (mode == "disable"):
    nova.services.disable_log_reason(host=cnname,binary="nova-compute",reason=reason)
    mlog(logf, 'Disabled the Compute Node '+cnname)
