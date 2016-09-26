
# Batch Deployment
  ##Installation

  Dynpart is available on INDIGO-1 repository (only for CentOS) at [location](http://repo.indigo-datacloud.eu/repository/indigo/1/centos7/x86_64/base/).
  
  Install the LSF side package:
  
 ####FROM RPM

You must have the epel repository enabled:

```$ yum install epel-release```

Then you have to enable the INDIGO - DataCloud packages repositories. See full instructions [here](https://indigo-dc.gitbooks.io/indigo-datacloud-releases/content/generic_installation_and_configuration_guide_1.html). Briefly you have to download the repo file from [INDIGO SW Repository](http://repo.indigo-datacloud.eu/repos/1/indigo1.repo) in your /etc/yum.repos.d folder.
```
$ cd /etc/yum.repos.d
$ wget http://repo.indigo-datacloud.eu/repos/1/indigo1.repo
```

Finally install the dynpart package.

```
$ yum install python-lsf-dynpart-partition-director
```

  On the LSF master, installing this package basically create and deploy following directories and files:

```
mkdir -p $LSF_TOP/var/tmp/cloudside/
mkdir -p $LSF_TOP/var/tmp/batchside/
mkdir -p $LSF_TOP/conf/scripts/dynpart/
cp dynp.conf elim.dynp esub.dynp bjobs_r.py LSF_TOP/conf/scripts/dynpart/
cp farm.json $LSF_TOP/var/tmp/cloudside/
ln -s $LSF_TOP/conf/scripts/dynpart/elim.dynp $LSF_SERVERDIR/elim.dynp
ln -s $LSF_TOP/conf/scripts/dynpart/esub.dynp $LSF_SERVERDIR/esub.dynp
```
### Retrieving the list of running batch jobs

The list of running jobs on each batch host can be achieved in two alternative ways:

1. Compiling the C program :

The **mcjobs_r.c** C program queries LSF through its APIs to retrieve the list of running jobs on each host. Pre compiled binary cannot be distributed due to licensing constraints, thus it must be compiled locally. Following is an example compile command, on LSF9.1; please adapt to your specific setup.

```
cd $LSF_TOP/conf/scripts/dynpart/
gcc mcjobs_r.c -I/usr/share/lsf/9.1/include/ /usr/share/lsf/9.1/linux2.6-glibc2.3-x86_64/lib/libbat.a /usr/share/lsf/9.1/linux2.6-glibc2.3-x86_64/lib/liblsf.a -lm -lnsl -ldl -o mcjobs_r
```

2. Python script :

Alternative to compiling the mcjobs_r.c is the **bjobs_r.py** script which produces the same result. It uses the batch command 'bjobs' to retrieve the number of running jobs on a given host.

### Edit LSF configuration files

*  In `/usr/share/lsf/conf/lsf.cluster.<clustername>` file check the host section.

  In the Host section specify usage of the dynp elim on each WN participating in the dynamic partitioning. Following is an example Host section:

```
Begin   Host
HOSTNAME  model    type server r1m  mem  swp  RESOURCES    #Keywords
#lsf master
lsf9test   !   !   1   3.5   ()   ()   (mg)
#Cloud Controller for Dynamic Partitioning
t1-cloudcc-02   ! ! 1 3.5 () () (mg)
wn-206-01-01-01-b ! ! 1 3.5 () () (dynp)
wn-206-01-01-02-b ! ! 1 3.5 () () (dynp)

End     Host```

* Define the dynp External Load Index In the Resource Section of `lsf.shared`:

```
Begin Resource
RESOURCENAME  TYPE    INTERVAL INCREASING  DESCRIPTION        # Keywords

   dynp    Numeric 60      Y        (dynpart: 1 batch, 2 cloud)

[....]
End Resource```

* Declare use of the custom ESUB method. Add the following in `lsf.conf`:

```
LSB_ESUB_METHOD="dynp"
```


> Note: The provided esub.dynp assumes that no other esub method is in place. If so, you must adapt it to your specific case.



* Verify LSF configuration is ok using the command:

```
lsadmin ckconfig

```

If everything is ok (no errors found) reconfigure and restart lim on
all nodes in the cluster:

[root@lsf9test ~]# lsadmin reconfig

Checking configuration files ...
No errors found.

Restart only the master candidate hosts? [y/n] n

Do you really want to restart LIMs on all hosts? [y/n] y

Restart LIM on <lsf9test> ...... done

Restart LIM on <t1-cloudcc-02> ...... done

Restart LIM on <wn-206-01-01-01-b> ...... done

Restart LIM on <wn-206-01-01-02-b> ...... done


Note: you can only manually restart lim on a subset of nodes, if
needed. For example, if you configure dynp for more nodes in
lsf.cluster.<clustername> cluster and want to make them partition
aware you can restrict limrestart to those nodes only.

Next, restart the Master Batch Daemon

[root@lsf9test ~]# badmin mbdrestart

Little after the header output line of the lsload -l command
will display the new External Load Information value dynp.

After some time (limrestart takes several minutes to take effect, even on a
small cluster) the value 1 should be reported by each node configured
to play dynp. other cluster members would display a dash.

### Dynp main component on LSF side:

- elim.dynp

This is a custom External Load Information Manager, specific to
LSF,created to enable implementation of the Functionalities and
conformant to the LSF guidelines. It assumes to be properly configured at batch system side.


### To simulate the concurrent activity following tool is provided:
  - submitter_demo.py
  
  keep submitting jobs to a specified queue



