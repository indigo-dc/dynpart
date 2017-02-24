class farm_dynpart::packages {
  
  $pkgs_list = [ 'python-lsf-dynpart-partition-director',
                 'python-dynpart-partition-director'
  ]

  $dep_list = [ 'python-novaclient',
                'python-neutronclient']
}
