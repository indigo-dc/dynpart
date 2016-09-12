#!/usr/bin/env python

import os
import sys
import time
import json

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

"""Common functions used by dynp scripts"""


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
        jc = json.load(open(json_file, 'r'))
    except ValueError:
        print "error while reading %s" % json_file
    except AttributeError:
        print "wrong json syntax : check your syntax in %s" % json_file
    except Exception, e:
        print str(e)
        sys.exit(0)
    return jc


def put_jsondict(json_file, json_dict):
    """Write back the updated dict to json file"""
    with open(json_file, 'w') as f:
        json.dump(json_dict, f)


def get_value(dict, key):
    val = dict.get(key, None)
    if not val:
        print "%s key not present in the dict, Plz check your conf file" % key
        sys.exit(1)
    return val
