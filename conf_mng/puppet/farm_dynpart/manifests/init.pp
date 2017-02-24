# Class: farm_dynpart
# ===========================
#
# Full description of class farm_dynpart here.
#
# Parameters
# ----------
#
# Document parameters here.
#
# * `sample parameter`
# Explanation of what this parameter affects and what it defaults to.
# e.g. "Specify one or more upstream ntp servers as an array."
#
# Variables
# ----------
#
# Here you should define a list of variables that this module would require.
#
# * `sample variable`
#  Explanation of how this variable affects the function of this class and if
#  it has a default. e.g. "The parameter enc_ntp_servers must be set by the
#  External Node Classifier as a comma separated list of hostnames." (Note,
#  global variables should be avoided in favor of class parameters as
#  of Puppet 2.6.)
#
# Examples
# --------
#
# @example
#    class { 'farm_dynpart':
#      servers => [ 'pool.ntp.org', 'ntp.local.company.com' ],
#    }
#
# Authors
# -------
#
# Author Name <author@domain.com>
#
# Copyright
# ---------
#
# Copyright 2017 Your name here, unless otherwise noted.
#
class farm_dynpart {
  include farm_dynpart::packages
  include farm_dynpart::repo

yumrepo { 'indigo_dynpart':
    baseurl  => 'http://repo.indigo-datacloud.eu/repository/indigo/1/centos7/x86_64/base/',
    gpgcheck => 0,
    descr    => 'Indigo Repository',
    enabled  => 1
  } -> 
  package { $dep_list: ensure => present } ->
    package { $pkgs_list: ensure => latest }
  
}

    file { '/etc/indigo/dynpart/dynp.conf':
        ensure => file,
        mode   => '0644',
        owner  => 'root',
        group  => 'root',
        source => 'puppet:///modules/farm_dynpart/dynp.conf'
    }
