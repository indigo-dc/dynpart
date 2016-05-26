#!/usr/bin/env python

import os,sys,time
import json
import commands
from novaclient.v2 import client

def now():
    """returns human readable date and time"""
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    """mlog(<file>,log message[,dbg=True]) -> append one log line to <file> if dbg == True"""
    if dbg:
        f.write("%s: "%now()+m+'\n')
        f.flush()

def get_jsondict(json_file):
    try:
        batch_cloud_dict = json.load(open(json_file,'r'))
    except:
#what should we do here
#        batch_cloud_dict = {'B':[],'C':[],'FB':[],'FC':[],'B2CR':[],'B2C':[],'C2B':[],'C2BR':[]}
        mlog(logf,"error parsing %s"%json_file)
    return batch_cloud_dict

def count_N_vm(hostN):
    for x in  nova.hypervisors.list():
        if (x.hypervisor_hostname==hostN):
            return x.running_vms

def make_switch(hostN,X,Y):
    X.append(hostN)
    while hostN in Y: Y.remove(hostN)
    return X,Y

def check_c2b(batch_cloud_dict):
    c2b_copy=batch_cloud_dict['C2B'][:]
    for hostN in c2b_copy:
        if exe_time <= batch_cloud_dict['C2B_TTL'][hostN]:
            count = count_N_vm(hostN)
            if count == 0:
                batch_cloud_dict['B'],batch_cloud_dict['C2B'] = make_switch(hostN,batch_cloud_dict['B'],batch_cloud_dict['C2B'])
                del batch_cloud_dict['C2B_TTL'][hostN]
        else:
            stop_running_vm(hostN)
            batch_cloud_dict['B'],batch_cloud_dict['C2B'] = make_switch(hostN,batch_cloud_dict['B'],batch_cloud_dict['C2B'])
            del batch_cloud_dict['C2B_TTL'][hostN]
    return batch_cloud_dict

def enable_nova(hostN):
    nova.services.enable(host=hostN, binary="nova-compute")

def check_b2c(batch_cloud_dict,RJ):
    b2c_copy=batch_cloud_dict['B2C'][:]
    for hostN in b2c_copy:
        HRJ = [x[:4] for x in RJ if x[3].find(hostN) >= 0]
        count = len(HRJ)
        if count == 0:
            batch_cloud_dict['C'],batch_cloud_dict['B2C'] = make_switch(hostN,batch_cloud_dict['C'],batch_cloud_dict['B2C'])
            enable_nova(hostN)
    return batch_cloud_dict

def stop_running_vm(hostN):   
    list_server_id=[x.id for x in nova.servers.list(search_opts={'host': hostN, 'all_tenants': 1})]
    for server_id in list_server_id:
        nova.servers.delete(server_id)


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

USERNAME = jc['USERNAME']
PASSWORD = jc['PASSWORD']
PROJECT_ID = jc['PROJECT_ID']
AUTH_URL = jc['AUTH_URL']
ttl_period = int(jc['ttl_period'])
log_dir = os.path.join(homedir,jc['log_dir'])
log_file = os.path.join(log_dir,jc['log_file'])

if not os.path.isdir(log_dir):
    print "%s log directory not found"%log_dir
    sys.exit(1)

logf = open(log_file,'a')

nova = client.Client(USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

exe_time = time.time()

"""Calculate the epoch seconds till TTL and write it on MJF file (described in conf file)"""
ttl = int(exe_time + ttl_period)

batch_cloud_json = os.path.join(json_dir, jc['batch_cloud_json']) 
batch_cloud_dict = get_jsondict(batch_cloud_json)

batch_cloud_dict['C2B']=list(set(batch_cloud_dict['C2BR']) | set(batch_cloud_dict['C2B']))
#consider user quotas (upper limit of no. of hosts in user area)
C2B = batch_cloud_dict['C2B']
for hostN in C2B:
    nova.services.disable_log_reason(host=hostN,binary="nova-compute",reason='test')
    if not batch_cloud_dict['C2B_TTL'].has_key(hostN):
        batch_cloud_dict['C2B_TTL'][hostN] = ttl
        job_features_dir = jc['machine_job_feature']['TTL_filepath']

        if not os.path.isdir(job_features_dir):
            os.mkdir(job_features_dir)

        job_features_file = hostN.replace('.','-')+'_ttl'
        jff = os.path.join(job_features_dir,job_features_file)
        try:
            jf = open(jff,'w')
            jf.write("%s"%ttl+'\n')
            jf.flush()
        except Exception,e:
            mlog(logf, str(e))
batch_cloud_dict['C'] = list(set(batch_cloud_dict['C']) - set(batch_cloud_dict['C2B']))   
batch_cloud_dict['C2BR']=[]

batch_cloud_dict['B2C']=list(set(batch_cloud_dict['B2CR']) | set(batch_cloud_dict['B2C']))
batch_cloud_dict['B'] = list(set(batch_cloud_dict['B']) - set(batch_cloud_dict['B2C']))
batch_cloud_dict['B2CR']=[]

mcjobs_r = jc["mcjobs_r"]
rj_file  = os.path.join(homedir, jc['rj_file'])

e,o = commands.getstatusoutput("""%s x > %s""" % (mcjobs_r,rj_file) )
if e and not o.endswith('No matching job found'):
    mlog(logf, "./mcjobs_r Failed!")
    sys.exit(0)
    
RJ = [x.rstrip().split(None,4) for x in open(rj_file,'r').readlines()]

batch_cloud_dict=check_c2b(batch_cloud_dict)
batch_cloud_dict=check_b2c(batch_cloud_dict,RJ)
        
with open(batch_cloud_json, 'w') as f:
        json.dump(batch_cloud_dict, f)
