# The classes that we 'include' are actually
# each defined in their own file. We must import
# them to have access to them.
import "classes/*"

stage { 'first': before => Stage['main'] }

class {
  'openhatch_dependencies': stage => first;
  'apt_get_update': stage => first
}


class openhatch_code {
  # Run bootstrap.py to make sure buildout can run
  exec { "/usr/bin/python2.6 /vagrant/bootstrap.py":
    creates => '/vagrant/bin/buildout',
    user => 'vagrant',
    group => 'vagrant',
    cwd => '/vagrant/',
  }

  exec { "/vagrant/bin/buildout":
    creates => '/vagrant/bin/mysite',
    user => 'vagrant',
    timeout => 0,
    group => 'vagrant',
    cwd => '/vagrant/',
    logoutput => true,
    require => [Exec["/usr/bin/python2.6 /vagrant/bootstrap.py"]],
  }

}

node default {
  include apt_get_update
  include openhatch_dependencies
  include openhatch_code
}