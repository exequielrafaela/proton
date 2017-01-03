# Import Fabric's API module#
from fabric.api import settings
from fabric.decorators import task
from fabric.operations import sudo


@task
def php53():
    """
Remove php-5.3.29 in a CentOS7 Server
    """
    with settings(warn_only=False):
        sudo('rm -rf /usr/local/bin/php')
        sudo('rm -rf /usr/local/bin/phpize')
        sudo('rm -rf /usr/local/bin/php-config')
        sudo('rm -rf /usr/local/include/php')
        sudo('rm -rf /usr/local/lib/php')
        sudo('rm -rf /usr/local/man/man1/php*')
        sudo('rm -rf /var/lib/php')
