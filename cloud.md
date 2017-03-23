# Cloud Deployment

## Installation

Dynpart is available on INDIGO-1 repository \(only for CentOS\) at [location](http://repo.indigo-datacloud.eu/repository/indigo/1/centos7/x86_64/base/).  Very soon we will have the INDIGO-2 release.

Install the cloud side package:

#### FROM RPM

You must have the epel repository enabled:

`$ yum install epel-release`

Then you have to enable the INDIGO - DataCloud packages repositories. See full instructions [here](https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/generic_installation_and_configuration_guide_1.html). Briefly you have to download the repo file from [INDIGO SW Repository](http://repo.indigo-datacloud.eu/repos/1/indigo1.repo) in your /etc/yum.repos.d folder.

```
$ cd /etc/yum.repos.d
$ wget http://repo.indigo-datacloud.eu/repos/1/indigo1.repo
```

Finally install the dynpart package.

```
$ yum install python-dynpart-partition-director
```

On the cloud controller, installing this package basically deploy following files:

```
/usr/bin/cn-manage.py
/usr/bin/create_instances.py
/usr/bin/delete_instance.py
/usr/bin/new_instance.py
/usr/bin/p_driver.py
/usr/bin/p_switch.py
/var/log/indigo/dynpart/dynpart.log
```

### The dynp configuration file

The main configuration file for the Dynamic Partitioning is the  
dynp.conf json file. BASEDIR for dynp in our case is _/usr/share/lsf/conf/scripts/dynpart _ which is based on local LSF environment.   
For instance the ’LSF\_ENVDIR' for LSF@CNAF is _/usr/share/lsf/conf_.

Dynamic partitioning must be configured properly via filling the _/etc/indigo/dynpart/dynp.conf_ which is eventually a link to   
_/usr/share/lsf/conf/scripts/dynpart/dynp.conf_

`$. ls -l /etc/indigo/dynpart/dynp.conf  
lrwxrwxrwx 1 root root 45 Jul  7 12:28 /etc/indigo/dynpart/dynp.conf -> /usr/share/lsf/conf/scripts/dynpart/dynp.conf`

json format does not allow comments in it. This document describes the configuration entries.

See below an example configuration dynp.conf with inline description. Note that comments are not allowed by json syntax, so they are only meant for documentation purpose.

```{
#auth section for Openstack user/project

"auth": {
#Name of the user with admin role
"USERNAME":"admin",
#Password of the user with admin role
"PASSWORD":"PASSWORD",
#Project id of the admin user
"PROJECT_ID":"admin",
#The keystone url
"AUTH_URL":"http://131.154.193.133:5000/v2.0",
#Name of the test user
"USERNAME_d":"demo",
#Password of the test user
"PASSWORD_d":"PASSWORD",
#Project id of the test user
"PROJECT_ID_d":"demo"
},

#
#log section. The path must exists on the machine running the dynpart 
#scripts (p_switch.py, p_driver.py)
#
"logging": {
#Path of the logging directory
"log_dir": "/var/log/indigo/dynpart/",
#Name of the log file
"log_file": "dynpart.log"
},

#
# switch section.
# The core configuration section
# 
"switch": {
# batch_cloud_json: this represents the Dynamic Partition JSON file containning the status
#information of each node, it must be readable by all nodes (Compute Nodes and Worker Nodes)
#
"batch_cloud_json":"/usr/share/lsf/var/tmp/cloudside/farm.json",
# bjobs_r: fullpath to an auxiliary program, whose output "rj_file"
# is used by p_driver.py. 
#
"bjobs_r": "/usr/share/lsf/conf/scripts/dynpart/bjobs_r",
#File containing the list of running jobs
"rj_file":"/usr/share/lsf/var/tmp/batchside/bjobs_r.out",
#
# ttl_period: When a Compute Node is selected for migration
# from Cloud to Batch, living VMs are to be removed before the
# role switching can happen. This task should be in charge to
# the cloud project using the VMs.
# Alternatively, a Time To Live can be defined, after that the VMs
# are destroyed by the partition manager. Default time to live period (5 mins) for VM
#
"ttl_period":"300"
},

#
# machine_job_feature: the above ttl_period value is written
# into a TTL_filepath directory, whose name matches the CNs name.
# A TTL_ENV_VAR environment variable is also set
# with the full pathname of the file
#
"machine_job_feature": {
#Path of the file containg the TTL value
"TTL_filepath":"/usr/share/lsf/var/tmp/cloudside",
#Name of the enviornment variable for  TTL
"TTL_ENV_VAR":"JOBFEATURES"
},

# VM section Only used by integration tools (such as
# create_instances.py) to test functionalities on a fresh install.
# This helps to simulate the workload of a cloud project
#
"VM_conf": {
#The image used for the VM
"image":"Fedora22",
#Name of the flavor
"flavor":"m1.large",
#Name of the keypair
"keyname":"demokey",
#Number of retries before exiting with error
"max_retries": 5,
#Custom sleeptime
"sleeptime": 5
},

# batch_submitter: batch section only used by integration tools (such
# as submitter_demo.py) to test functionalities on a fresh install.
# This helps to simulate the workload of a cloud project.  These are
# parameters for the submitter_demo.py tool, which are used to submit
# sleep jobs to a named queue. the tool submit jobs until max_pend are
# queued, then keeps submitting again when less then min_pend jobs are
# queued. Each job takes a random sleep time with avg_sleep seconds on
# average. After each submission cycle the submitter sleeps for nap
# seconds.
#
"batch_submitter": {
"queue": "short",
"max_pend": 300,
"avg_sleep": 280,
"nap": 5
}

}
```

The following describes the meaning of the attributes of the dynp configuartion file, for each subsection:

**Section\[auth\]**

| Attribute | Description |
| --- | --- |
| USERNAME | The name of the username with the admin role |
| PASSWORD | The password of the above specified user with the admin role |
| PROJECT\_ID | The project to request authorization on |
| AUTH\_URL | The URL of the Openstack identity service |
| USERNAME\_d | The name of the standard user |
| PASSWORD\_d | The password of the above specified user |
| PROJECT\_ID\_d | The project id of standard user |

**Section\[logging\]**

| Attribute | Description |
| --- | --- |
| log\_dir | Absolute path of the directory where the log file resides |
| log\_file | The name of the log file |

**Section\[VM\_conf\]**

| Attribute | Description |
| --- | --- |
| image | The image used for the VM. A virtual machine image, is a single file that contains a virtual disk that has a bootable operating system installed on it. Images are used to create virtual machine instances within the cloud. |
| flavor | The name of the flavor. Virtual hardware templates are called "flavors" in OpenStack, defining sizes for RAM, disk, number of cores, and so on. |
| keyname | The name of the keypair. One can access via ssh the VM using this key pair. |
| max\_retries | This number specifies the number of retries nova does to instantiate a VM before giving up and exiting together with releasing the assigned IP. |
| sleeptime | customized sleeptime which is used within many operations |

**Section\[switch\]**

| Attribute | Description |
| --- | --- |
| batch\_cloud\_json | Path of the JSON file containing the status of each node specifying wheather the node belongs to Batch or Cloud or is in an transitory state which can be C2B \(Cloud to batch\) or B2C \(Batch to Cloud\) |
| bjobs\_r | Path of the script which calculates the number of running batch jobs on a given batch cluster |
| rj\_file | The result of the above script is stored in this file |
| ttl\_period | Default time-to-live \(TTL\) period for VM in seconds. After spanning ttl\_period all the VM's on a given compute node will be killed. |

**Section\[machine\_job\_feature\]**

| Attribute | Description |
| --- | --- |
| TTL\_filepath | Path of the file containing the TTL value, it is stored in the shared file system and it is assumed that each VM knows this path. |
| TTL\_ENV\_VAR | System enviornment variable which stores the value of TTL |

**Section\[batch\_submitter\]**

| Attribute | Description |
| --- | --- |
| queue | Submit sleep jobs on a given batch queue |
| max\_pend | Maximum number of pending jobs until which it keeps on submitting sleep jobs |
| avg\_sleep | The average sleep time for each job |
| nap | The small nap period between each submission cycle |

## Two main components on Cloud side:

* `p_switch.py  <to_cloud|to_batch> <filename>`

This tool triggers role switching for hosts from Batch to Cloud or vice-versa.  It is provided with a file contining a list of hostnames whose role is to be switched

* `p_driver.py`

This script checks for status changes of each host under transition and takes needed action accordingly. For example, when a host switching from Batch to Cloud has no more running jobs, it is enabled to Openstack as hypervisor, and from then on, new VM can be instantiated there by the Nova component.

### To simulate the concurrent activity following tool is provided:

* create\_instances.py

  keep requesting VM instantiation to openstack at a regular rate



