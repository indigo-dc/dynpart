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
    script_name =  os.path.basename(sys.argv[0])
    if dbg:
        f.write("%s %s:"%(now(), script_name)+m+'\n')
        f.flush()

def get_jsondict(json_file):
    """get_jsondict(<file>) -> Returns python dictionary object from JSON file """
    try:
        batch_cloud_dict = json.load(open(json_file,'r'))
    except:
#what should we do here
#        batch_cloud_dict = {'B':[],'C':[],'FB':[],'FC':[],'B2CR':[],'B2C':[],'C2B':[],'C2BR':[]}
        print "error parsing %s"%json_file
        mlog(logf,"error parsing %s"%json_file)
    return batch_cloud_dict

def count_N_vm(hostN):
    """count_N_vm(<host>) -> Returns the number of running VM's on <host>"""
    for x in  nova.hypervisors.list():
        if (x.hypervisor_hostname==hostN):
            return x.running_vms

def make_switch(hostN,X,Y):
    """make_switch(<host>,list X,list Y) -> Switch the <host> from list X to list Y i.e append <host> to list X and removes the same from list Y and returns the updated lists """
    X.append(hostN)
    while hostN in Y: Y.remove(hostN)
    return X,Y

def check_c2b(batch_cloud_dict):
    """check_c2b(<dict>) -> Checks each host in C2B if it is ready for switch and makes the switch when either host has #VM's = 0 or time now > TTL, Returns the updated <dict>"""
    job_features_dir = jc['machine_job_feature']['TTL_filepath']
    c2b_copy=batch_cloud_dict['C2B'][:]
    for hostN in c2b_copy:
        shutdown_file = hostN.replace('.','-')+'_ttl'
        sdf = os.path.join(job_features_dir,shutdown_file)
        if exe_time <= batch_cloud_dict['C2B_TTL'][hostN]:
            count = count_N_vm(hostN)
            if count == 0:
                print "No of running VM on %s is %d"%(hostN,count)
                mlog(logf,"No of running VM on %s is %d"%(hostN,count))
                print "Moving %s from list C2B to B"%hostN
                mlog(logf,"Moving %s from list C2B to B"%hostN)
                batch_cloud_dict['B'],batch_cloud_dict['C2B'] = make_switch(hostN,batch_cloud_dict['B'],batch_cloud_dict['C2B'])
                del batch_cloud_dict['C2B_TTL'][hostN]
                os.remove(sdf)
        else:
            print "TTL has expired since %d > %d"%(exe_time,batch_cloud_dict['C2B_TTL'][hostN])
            mlog(logf,"TTL has expired since %d > %d"%(exe_time,batch_cloud_dict['C2B_TTL'][hostN]))
            stop_running_vm(hostN)
            print "Moving %s from list C2B to B"%hostN
            mlog(logf,"Moving %s from list C2B to B"%hostN)
            batch_cloud_dict['B'],batch_cloud_dict['C2B'] = make_switch(hostN,batch_cloud_dict['B'],batch_cloud_dict['C2B'])
            del batch_cloud_dict['C2B_TTL'][hostN]
            os.remove(sdf)
    return batch_cloud_dict

def enable_nova(hostN):
    """enable_nova(<host>) -> Enables nova service on <host> """
    nova.services.enable(host=hostN, binary="nova-compute")
    print "Enabled nova service on %s"%hostN
    mlog(logf,"Enabled nova service on %s"%hostN)

def disable_nova(hostN):
    """disable_nova(<host>) -> Disables nova service on <host> """
    nova.services.disable_log_reason(host=hostN,binary="nova-compute",reason='test')
    print "Disabled nova service on %s"%hostN
    mlog(logf,"Disabled nova service on %s"%hostN)


def check_b2c(batch_cloud_dict):
    """check_b2c(<dict>) -> Checks each host in B2C if it is ready for switch and makes the switch when host has #Running_jobs = 0, Returns the updated <dict>"""
    mcjobs_r = jc["mcjobs_r"]
    rj_file  = os.path.join(homedir, jc['rj_file'])
    cmd = """%s x > %s""" % (mcjobs_r,rj_file)
    print "Executing",cmd
    e,o = commands.getstatusoutput(cmd)
#    print "ciao"
#    print e,o
    if e or o.endswith('No matching job found'):
        mlog(logf, "./mcjobs_r Failed!")
#Need to understand better what to do here
#        sys.exit(0)

#    print "ciao1"
    RJ = [x.rstrip().split(None,4) for x in open(rj_file,'r').readlines()]
    b2c_copy = batch_cloud_dict['B2C'][:]
    for hostN in b2c_copy:
        hostname=hostN.partition('.')[0]
        HRJ = [x[:4] for x in RJ if x[3].find(hostname) >= 0]
        count = len(HRJ)
        if count == 0:
            print "No of jobs running on %s is %d"%(hostN,count)
            mlog(logf,"No of jobs running on %s is %d"%(hostN,count))
            print "Moving %s from list B2C to C"%hostN
            mlog(logf,"Moving %s from list B2C to C"%hostN)
            batch_cloud_dict['C'],batch_cloud_dict['B2C'] = make_switch(hostN,batch_cloud_dict['C'],batch_cloud_dict['B2C'])
            enable_nova(hostN)
        else:
            print "No of jobs running on %s is %d"%(hostN,count)
            mlog(logf,"No of jobs running on %s is %d"%(hostN,count))
            print "Not moving %s to list C"%hostN
            mlog(logf,"Not moving %s to list C"%hostN)

    return batch_cloud_dict

def stop_running_vm(hostN):
    """stop_running_vm(<host>) -> Stop all the running VM's on <host> """
    list_server_id=[x.id for x in nova.servers.list(search_opts={'host': hostN, 'all_tenants': 1})]
    for server_id in list_server_id:
        nova.servers.delete(server_id)
    print "Stopped and deleted all the VM on %s"%hostN
    mlog(logf,"Stopped and deleted all the VM on %s"%hostN)

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
ttl = int(exe_time + ttl_period)

batch_cloud_json = os.path.join(json_dir, jc['batch_cloud_json']) 
batch_cloud_dict = get_jsondict(batch_cloud_json)

batch_cloud_dict['C2B']=list(set(batch_cloud_dict['C2BR']) | set(batch_cloud_dict['C2B']))
#consider user quotas (upper limit of no. of hosts in user area)
C2B = batch_cloud_dict['C2B']
for hostN in C2B:
    disable_nova(hostN)
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

batch_cloud_dict=check_c2b(batch_cloud_dict)
batch_cloud_dict=check_b2c(batch_cloud_dict)
        
with open(batch_cloud_json, 'w') as f:
        json.dump(batch_cloud_dict, f)
