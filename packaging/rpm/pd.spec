Name:          python-dynpart-partition-director
Version:       0.08
Release:       1%{?dist}
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


%prep
%setup -q


%build
#%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
#%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

install -d -m0755                           %{buildroot}%{_localstatedir}/log/indigo/dynpart
touch                                       %{buildroot}%{_localstatedir}/log/indigo/dynpart/dynpart.log
install -D -m0755 bin/new_instance.py       %{buildroot}%{_bindir}/new_instance.py
install -D -m0755 bin/create_instances.py   %{buildroot}%{_bindir}/create_instances.py
install -D -m0755 bin/delete_instance.py    %{buildroot}%{_bindir}/delete_instance.py
install -D -m0755 bin/cn-manage.py          %{buildroot}%{_bindir}/cn-manage.py
install -D -m0755 bin/p_switch.py           %{buildroot}%{_bindir}/p_switch.py
install -D -m0755 bin/p_driver.py           %{buildroot}%{_bindir}/p_driver.py

%files
#%{python_sitelib}/*
%defattr(-,root,root,-)
%{_bindir}/new_instance.py
%{_bindir}/create_instances.py
%{_bindir}/delete_instance.py
%{_bindir}/cn-manage.py
%{_bindir}/p_switch.py
%{_bindir}/p_driver.py
%{_localstatedir}/log/indigo/dynpart/dynpart.log


%changelog
