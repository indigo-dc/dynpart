#!/usr/bin/env python

import os
import sys
import time
import json

"""
Makes the initial preperation of json dictionary and switch/moves the nodes
 to a particular set depending on the request i.e FROM/TO batch/cloud

Usage: p_switch.py to_batch|to_cloud filename

"""

"""
Algorithm

Assume: Status of nodes is defined in a given json file and
list of nodes to switch is provided in a file via commandline

Take: Json dictionary from json file and list of nodes to switch
from file via commandline

Does: Makes the initial preperation of json dictionary and switch/moves
the nodes to a particular set depending on the request i.e FROM/TO batch/cloud
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


def get_jsondict(json_file):
    """get_jsondict(<json_file>) ->
    Returns python dictionary object from JSON file"""
    try:
        batch_cloud_dict = json.load(open(json_file, 'r'))
    except:
        mlog(logf, "error parsing %s" % json_file)
        sys.exit(0)
    return batch_cloud_dict


def help():
    print """"usage: p_switch.py to_batch|to_cloud filename\n
    Makes the initial preperation of json dictionary and switch/moves the nodes
    to a particular set depending on the request i.e FROM/TO batch/cloud
"""

if len(sys.argv) <= 2:
    help()
    sys.exit(0)

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

log_dir = jc['logging']['log_dir']
log_file = os.path.join(log_dir, jc['logging']['log_file'])
batch_cloud_json = jc['switch']['batch_cloud_json']
batch_cloud_dict = get_jsondict(batch_cloud_json)

if not os.path.isdir(log_dir):
    print "%s file not found" % log_dir
    sys.exit(1)

logf = open(log_file, 'a')
have_args = len(sys.argv) > 1
if have_args:
    opt = sys.argv[1]
    match = (opt in ['to_cloud', 'to_batch'])
    if not match:
        mlog(logf, "Option doesn't match, options are : to_cloud or to_batch")
        sys.exit(0)
    if opt == 'to_cloud':
        to_cloud_file = sys.argv[2]
        to_batch_file = ''
        if not os.path.isfile(to_cloud_file):
            mlog(logf, "Please check the path of the file")
            sys.exit(1)

        try:
            """Creats the set B2CR from the nodes in the file"""
            B2CR = set(
                [x for x in open(to_cloud_file, 'r').read().split() if x])
        except:
            mlog(logf, "Error while parsing %s" % to_cloud_file)
            B2CR = set()
        """Firstly B2CR should not include the nodes which are already in list C and
Secondly it should contain unique elements from present and past requests"""
        if not B2CR.isdisjoint(set(batch_cloud_dict['C'])):  # intersection
            already_in_C = B2CR.intersection(set(batch_cloud_dict['C']))
            for node in already_in_C:
                mlog(logf, "Node: %s is already in C set-Doing Nothing" % node)
        B2CR = B2CR - set(batch_cloud_dict['C'])
        batch_cloud_dict['B2CR'] = list(set(batch_cloud_dict['B2CR']) | B2CR)
        for hostname in batch_cloud_dict['B2CR']:
            mlog(logf, "Moving node %s to B2CR" % hostname)
        """Write back the updated dict to json file"""
        with open(batch_cloud_json, 'w') as f:
            json.dump(batch_cloud_dict, f)
        # os.remove(to_cloud_file)#commented until testing

    elif opt == 'to_batch':
        to_batch_file = sys.argv[2]
        to_cloud_file = ''
        if not os.path.isfile(to_batch_file):
            mlog(logf, "Please check the path of the file")
            sys.exit(1)
        try:
            """Creats the set C2BR from the nodes in the file"""
            C2BR = set(
                [x for x in open(to_batch_file, 'r').read().split() if x])
        except:
            mlog(logf, "Error while parsing %s" % to_batch_file)
            C2BR = set()
        """Firstly C2BR should not include the nodes which are already in list B and
Secondly it should contain unique elements from present and past requests"""
        if not C2BR.isdisjoint(set(batch_cloud_dict['B'])):  # intersection
            already_in_B = C2BR.intersection(set(batch_cloud_dict['B']))
            for node in already_in_B:
                mlog(logf, "Node: %s is already in B set-Doing Nothing" % node)
        C2BR = C2BR - set(batch_cloud_dict['B'])
        batch_cloud_dict['C2BR'] = list(set(batch_cloud_dict['C2BR']) | C2BR)
        for hostname in batch_cloud_dict['C2BR']:
            mlog(logf, "Moving node %s to C2BR" % hostname)
        """Write back the updated dict to json file"""
        with open(batch_cloud_json, 'w') as f:
            json.dump(batch_cloud_dict, f)
        # os.remove(to_batch_file)#commented until testing
