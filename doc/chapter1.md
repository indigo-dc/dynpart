


## Dynamic partition Working principles

Physical machines are members of a Batch System cluster (LSF) and a
Cloud (Openstack) cluster at the same time; furthermore, they can only be
active in a mutually exclusive manner on one and one only cluster at
any time. This implicitly defines a partition of hosts active at batch
or cloud side.

We refer to active Hosts in the batch partition as "Worker Nodes", and
to active hosts in the cloud partition as "Compute Nodes".

A **Partition driver** is a software component dealing with transition
requests: it performs the needed steps to convert a host from WN to CN
or from CN to WN. Note that nodes are not removed from one cluster, nor
joined the another; they are simply made active on the target cluster and
inactive in the origin cluster.

To do so:

*  At cloud side

  *  Compute Nodes are Enabled / Disabled using OpenStack APIs

* At Batch side

  * Worker Nodes are configured to publish a numeric status value
   (External Load Index) named dynp, indicating the partition they
   belong to.

  * LSF Master is configured to alter job parameters at submission time,
   adding the requirement for a node having the correct value of dynp




## Deployment instructions


###  Assumptions

This guide assumes that:

- A properly configured Batch System instance is operational
  (currently LSF, version 7.x or newer)

- A working OpenStack instance is in place, with a Cloud Controller as
  privileged member of the LSF cluster.

- Cluster members (WN and CN) have read access to a shared filesystem
 ( mounted as 
> LSF_TOP=/usr/share/lsf

 for the sake of example )
 
 In next sections we describe the Batch side and Cloud side deployment instructions seperately.