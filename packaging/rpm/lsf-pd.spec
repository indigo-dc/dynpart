Name:          python-lsf-dynpart-partition-director
Version:       0.08
Release:       1%{?dist}
Summary:       LSF side scripts for Partition Director
License:       Apache Software License
Source:        %name-%version.tar.gz
Vendor:        INDIGO - DataCloud

BuildArch:     noarch
BuildRequires: python-devel
BuildRequires: python-setuptools


%description
Set of scripts and configuration files deployed on/by the LSF master. Partition Director ease management of a hybrid data center, where both Batch System based and cloud based services are provided. Physical computing resources can play both roles in a mutual exclusive fashion. The Partition Director takes care of commuting the role of one or more physical machines from "Worker Node" (member of the batch system cluster) to "Compute Node" (member of a cloud instance) and vice versa.


%prep
%setup -q


%build

%install
rm -rf $RPM_BUILD_ROOT

install -d -m0755                           %{buildroot}%{_sysconfdir}/indigo/dynpart
install -d -m0755                           %{buildroot}%{getenv:LSF_ENVDIR}/scripts/dynpart
install -D -m0644 etc/dynp.conf        %{buildroot}%{getenv:LSF_ENVDIR}/scripts/dynpart/dynp.conf
install -D -m0755 batch/esub.dynp.template  %{buildroot}%{getenv:LSF_ENVDIR}/scripts/dynpart/esub.dynp
install -D -m0755 batch/elim.dynp        %{buildroot}%{getenv:LSF_ENVDIR}/scripts/dynpart/elim.dynp
install -D -m0644 batch/mcjobs_r.c        %{buildroot}%{getenv:LSF_ENVDIR}/scripts/dynpart/mcjobs_r.c
install -d -m0755     %{buildroot}%{_usr}/share/lsf/var/tmp/cloudside
install -D -m0644 etc/farm.json       %{buildroot}%{_usr}/share/lsf/var/tmp/cloudside/farm.json
install -D -m0755 bin/submitter_demo.py     %{buildroot}%{_bindir}/submitter_demo.py


%files
%defattr(-,root,root,-)
%config(noreplace) %{getenv:LSF_ENVDIR}/scripts/dynpart/dynp.conf
%{getenv:LSF_ENVDIR}/scripts/dynpart
%{getenv:LSF_ENVDIR}/scripts/dynpart/esub.dynp
%{getenv:LSF_ENVDIR}/scripts/dynpart/elim.dynp
%{getenv:LSF_ENVDIR}/scripts/dynpart/mcjobs_r.c
%{_usr}/share/lsf/var/tmp/cloudside
%{_usr}/share/lsf/var/tmp/cloudside/farm.json
%{_bindir}/submitter_demo.py

%post
ln -s   %{getenv:LSF_ENVDIR}/scripts/dynpart/dynp.conf %{_sysconfdir}/indigo/dynpart/dynp.conf
ln -s   %{getenv:LSF_ENVDIR}/scripts/dynpart/esub.dynp.template %{getenv:LSF_SERVERDIR}/esub.dynp
ln -s   %{getenv:LSF_ENVDIR}/scripts/dynpart/elim.dynp %{getenv:LSF_SERVERDIR}/elim.dynp

%changelog
