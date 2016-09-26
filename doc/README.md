# Dynamic Partitioning - Partition Director

Partition Director ease management of a hybrid data center, where both Batch System based and cloud based services are provided. Physical computing resources can play both roles in a mutual exclusive fashion.

The Partition Director takes care of commuting the role of one or more physical machines from "Worker Node" (member of the batch system cluster) to "Compute Node" (member of a cloud instance) and vice versa.

Current release only works with the IBM/Platform LSF Batch system (version 7.0x or higher) and Openstack Cloud manager instances (Kilo or newer).


### Functionalities:

- switch role of selected physical machines from the LSF cluster to
  the Openstack one.

- switch role of selected physical machines from the Openstack cluster
  to the LSF one.

- manage intermediate transition statuses, ensure consistency