#!/usr/bin/env python

import os
import sys
import time
import getopt
import json
from novaclient.v2 import client

"""
Manage nova compute service i.e enable/disable compute service on CN
Usage:
python cn-manage.py --mode=enable --cnname=wn-name --reason="test" OR
python cn-manage.py -mode enable -c wn-name -r "test"'''

"""

"""
Algorithm

Take: The authentication parameters from the conf file
and mode=enable|diable, CN name and reason from cmdline
Action: Enable|disable the nova compute service on CN for a defined reason

"""
# TODO : make stong and error free argument matching

mode = ''
cnname = ''
reason = ''

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
    print """Usage: python cn-manage.py --mode=enable --cnname=wn-name --reason="test" OR
    python cn-manage.py -m enable -c wn-name -r "test"
    Enable|disable the nova compute service on CN for a defined reason
"""

try:
    opts, args = getopt.getopt(sys.argv[1:], "hm:c:r:", [
                               "mode=", "cnname=", "reason="])
except getopt.GetoptError:
    help()
    sys.exit(2)

if len(sys.argv) <= 6:
    help()
    sys.exit(0)

for opt, arg in opts:
    if opt == '-h':
        help()
        sys.exit()
    elif opt in ("-m", "--mode"):
        mode = arg
    elif opt in ("-c", "--cnname"):
        cnname = arg
    elif opt in ("-r", "--reason"):
        reason = arg

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
USERNAME = jc['auth']['USERNAME']
PASSWORD = jc['auth']['PASSWORD']
PROJECT_ID = jc['auth']['PROJECT_ID']
AUTH_URL = jc['auth']['AUTH_URL']

log_dir = jc['logging']['log_dir']
log_file = os.path.join(log_dir, jc['logging']['log_file'])

if not os.path.isdir(log_dir):
    print "%s log directory not found" % log_dir
    sys.exit(1)

logf = open(log_file, 'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

"""Enabling/Disabling the compute service on host"""
if (mode == "enable"):
    nova.services.enable(host=cnname, binary="nova-compute")
    mlog(logf, "Enabled the Compute Node " + cnname)
elif (mode == "disable"):
    nova.services.disable_log_reason(
        host=cnname, binary="nova-compute", reason=reason)
    mlog(logf, 'Disabled the Compute Node ' + cnname)
