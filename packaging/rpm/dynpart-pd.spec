%define _lsfenvdir /usr/share/lsf/conf

Name:          python-dynpart-partition-director
Version:       0.9
Release:       2%{?dist}
Summary:       Partition Director of batch and cloud resources
License:       Apache Software License
Source:        %name-%version.tar.gz
Vendor:        INDIGO - DataCloud


BuildArch:     noarch
BuildRequires: python-devel
BuildRequires: python-setuptools
Requires:      python-novaclient
Requires:      python-neutronclient

%description
Set of scripts on the cloud controller. Partition Director ease management of a hybrid data center, where both Batch System based and cloud based services are provided. Physical computing resources can play both roles in a mutual exclusive fashion. The Partition Director takes care of commuting the role of one or more physical machines from "Worker Node" (member of the batch system cluster) to "Compute Node" (member of a cloud instance) and vice versa.

%package cc
Summary:       Set of scripts on the cloud controller
%description cc
This contains the set of scripts needed on the cloud controller. Partition Director ease management of a hybrid data center, where both Batch System based and cloud based servic are provided. Physical computing resources can play both roles in a mutual exclusive fashion. The Partition Director takes care of commuting the role of one or more physical machines from "Worker Node" (member of the batch system cluster) to "Compute Node" (member of a cloud instance) and vice versa.

%package lsf
Summary:       Set of scripts and configuration files deployed on/by the LSF master
%description lsf 
This contains the set of scripts and configuration files deployed on/by the LSF master. Partition Director ease management of a hybrid data center, where both Batch System based and cloud based services are provided. Physical computing resources can play both roles in a mutual exclusive fashion. The Partition Director takes care of commuting the role of one or more physical machines from "Worker Node" (member of the batch system cluster) to "Compute Node" (member of a cloud instance) and vice versa.

%prep
%setup -q


%build

%install
rm -rf $RPM_BUILD_ROOT

install -d -m0755                           %{buildroot}%{_localstatedir}/log/indigo/dynpart
touch                                       %{buildroot}%{_localstatedir}/log/indigo/dynpart/dynpart.log
install -D -m0755 bin/new_instance.py       %{buildroot}%{_bindir}/new_instance.py
install -D -m0755 bin/create_instances.py   %{buildroot}%{_bindir}/create_instances.py
install -D -m0755 bin/delete_instance.py    %{buildroot}%{_bindir}/delete_instance.py
install -D -m0755 bin/cn-manage.py          %{buildroot}%{_bindir}/cn-manage.py
install -D -m0755 bin/p_switch.py           %{buildroot}%{_bindir}/p_switch.py
install -D -m0755 bin/p_driver.py           %{buildroot}%{_bindir}/p_driver.py

install -d -m0755                           %{buildroot}%{_sysconfdir}/indigo/dynpart
install -d -m0755                           %{buildroot}%{_lsfenvdir}/scripts/dynpart
install -D -m0644 etc/dynp.conf             %{buildroot}%{_lsfenvdir}/scripts/dynpart/dynp.conf
install -D -m0644 etc/dynp.conf.template    %{buildroot}%{_lsfenvdir}/scripts/dynpart/dynp.conf.template
install -D -m0755 batch/esub.dynp.template  %{buildroot}%{_lsfenvdir}/scripts/dynpart/esub.dynp
install -D -m0755 batch/elim.dynp           %{buildroot}%{_lsfenvdir}/scripts/dynpart/elim.dynp
install -D -m0644 batch/bjobs_r.py          %{buildroot}%{_lsfenvdir}/scripts/dynpart/bjobs_r.py
install -d -m0755                           %{buildroot}%{_usr}/share/lsf/var/tmp/cloudside
install -D -m0644 etc/farm.json             %{buildroot}%{_usr}/share/lsf/var/tmp/cloudside/farm.json
install -D -m0755 bin/submitter_demo.py     %{buildroot}%{_bindir}/submitter_demo.py
install -D -m0755 bin/adjust_lsf_shares.py  %{buildroot}%{_bindir}/adjust_lsf_shares.py

%files cc
%defattr(-,root,root,-)
%{_bindir}/new_instance.py
%{_bindir}/create_instances.py
%{_bindir}/delete_instance.py
%{_bindir}/cn-manage.py
%{_bindir}/p_switch.py
%{_bindir}/p_driver.py
%{_localstatedir}/log/indigo/dynpart/dynpart.log

%files lsf
%defattr(-,root,root,-)
%config(noreplace) %{_lsfenvdir}/scripts/dynpart/dynp.conf
%{_lsfenvdir}/scripts/dynpart
%{_lsfenvdir}/scripts/dynpart/dynp.conf.template
%{_lsfenvdir}/scripts/dynpart/esub.dynp
%{_lsfenvdir}/scripts/dynpart/elim.dynp
%{_lsfenvdir}/scripts/dynpart/bjobs_r.py
%{_usr}/share/lsf/var/tmp/cloudside
%{_usr}/share/lsf/var/tmp/cloudside/farm.json
%{_bindir}/submitter_demo.py
%{_bindir}/adjust_lsf_shares.py

%changelog cc

%changelog lsf
