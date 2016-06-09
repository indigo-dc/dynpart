#!/usr/bin/env python
"""
CLOUD Makes the initial preperation of json dictionary for the switch request FROM/TO batch/cloud and sets and starts the TTL clock
Usage: p_switch.py to_batch|to_cloud filename

"""
import os,sys,time
import json

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    script_name =  os.path.basename(sys.argv[0])
    if dbg:
        f.write("%s %s:"%(now(), script_name)+m+'\n')
        f.flush()

def get_jsondict(json_file):
    """get_jsondict(<json_file> -> Returns the dictionary with json file contents, in case of error returns empty dictionary"""
    try:
        batch_cloud_dict = json.load(open(json_file,'r'))
    except:
        #what should we do here
        #batch_cloud_dict = {'B':[],'C':[],'FB':[],'FC':[],'B2CR':[],'B2C':[],'C2B':[],'C2BR':[]}
        mlog(logf,"error parsing %s"%json_file)
    return batch_cloud_dict

def help():
    print """"usage: p_switch.py to_batch|to_cloud filename\n
moves switches roles for hostnames in the given filenam
"""

if len(sys.argv) == 1:
    help()
    sys.exit(0)

homedir = '/home/TIER1/sdalpra/demo/'
conf_dir = os.path.join(homedir,"etc/")
conf_file = os.path.join(conf_dir,'dynp.conf')
json_dir = "/usr/share/lsf/conf/scripts/dynpart/"

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

log_dir = os.path.join(homedir,jc['log_dir'])
log_file = os.path.join(log_dir,jc['log_file'])

if not os.path.isdir(log_dir):
    print "%s file not found"%log_dir
    sys.exit(1)

logf = open(log_file,'a')

batch_cloud_json = os.path.join(json_dir, jc['batch_cloud_json'])
batch_cloud_dict = get_jsondict(batch_cloud_json)

have_args = len(sys.argv) > 1
if have_args:
    opt = sys.argv[1]
    match = (opt in ['to_cloud', 'to_batch'])
    if not match:
        print "Option doesn't match, options are : to_cloud or to_batch"
        mlog(logf,"Option doesn't match, options are : to_cloud or to_batch")
        sys.exit(0)
    if opt == 'to_cloud':
        to_cloud_file = os.path.join(homedir,sys.argv[2])
        to_batch_file =''
        if os.path.isfile(to_cloud_file):
            try:
                """Creats the set B2CR from the hostnames in the file"""
                B2CR = set([x for x in open(to_cloud_file,'r').read().split() if x])
            except:
                print "Error while parsing %s"%to_cloud_file
                mlog(logf,"Error while parsing %s"%to_cloud_file)
                B2CR = set()
            #"""1)B2CR should not include the hostname which are already in list C and 2)Contains unique elements from present and past requests"""
            if not B2CR.isdisjoint(set(batch_cloud_dict['C'])): #intersection
                already_in_C = B2CR.intersection(set(batch_cloud_dict['C']))
                for node in already_in_C:
                    print "Node: %s is already in C set - Doing Nothing" %node
                    mlog(logf,"Node: %s is already in C set - Doing Nothing" %node)
            B2CR = B2CR - set(batch_cloud_dict['C'])
            batch_cloud_dict['B2CR'] = list(set(batch_cloud_dict['B2CR']) | B2CR)
            for hostname in batch_cloud_dict['B2CR']:
                print "Moving node %s to B2CR" % hostname
                mlog(logf,"Moving node %s to B2CR" % hostname)
            """Write back the updated dict to json file"""
            with open(batch_cloud_json, 'w') as f:
                json.dump(batch_cloud_dict, f)
            #os.remove(to_cloud_file)#commented until testing
        else:
            print "Please check the path of the file"
            mlog(logf,"Please check the path of the file")
        
    elif opt == 'to_batch':
        to_batch_file = os.path.join(homedir,sys.argv[2])
        to_cloud_file = ''
        if os.path.isfile(to_batch_file):
            try:
                """Creats the set C2BR from the hostnames in the file"""
                C2BR = set([x for x in open(to_batch_file,'r').read().split() if x])
            except:
                mlog(logf,"Error while parsing %s"%to_batch_file)
                C2BR = set()
            #"""1)C2BR should not include the hostname which are already in list B and 2)Contains unique elements from present and past requests"""
            if not C2BR.isdisjoint(set(batch_cloud_dict['B'])): #intersection
                already_in_B = C2BR.intersection(set(batch_cloud_dict['B']))
                for node in already_in_B:
                    print "Node: %s is already in B set - Doing Nothing" %node
                    mlog(logf,"Node: %s is already in B set - Doing Nothing" %node)
            C2BR = C2BR - set(batch_cloud_dict['B'])
            batch_cloud_dict['C2BR'] = list(set(batch_cloud_dict['C2BR']) | C2BR)
            for hostname in batch_cloud_dict['C2BR']:
                print "Moving node %s to C2BR" % hostname
                mlog(logf,"Moving node %s to C2BR" % hostname)
            """Write back the updated dict to json file"""
            with open(batch_cloud_json, 'w') as f:
                json.dump(batch_cloud_dict, f)
            #os.remove(to_batch_file)#commented until testing
        else:
            mlog(logf,"Please check the path of the file")
