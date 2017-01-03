# Import Fabric's API module#
from fabric.api import settings
from fabric.decorators import task
from termcolor import colored

from modules import key_fab
from modules import rsync_fab


@task
def upload_lamp_from_server(data_dir, remote_dir):
    """
Upload LAMP stack data using rsync_data_to_server_v2 task
    :param data_dir: Directory where the data it's locally stored
    :param remote_dir: Remote dir to store the LAMP stack data and conf

IMPORTANT 1:
Remeber to genereta a key pair for root, if the key does not exists this task won't work
since it's a MANDATORY PREREQUISITE for it. Then, before executing it, you should use:
"fab -R local key_gen:root"
"fab -R devtest key_append:root"

IMPORTANT 2:
To mantain the files permissions you must run this taks with sudo:
eg:sudo fab -R devtest upload_lamp_from_server:/tmp/172.28.128.4/,/tmp/

IMPORTANT 3:
It's a must to have in every server the rsync package already installed!
    """
    with settings(warn_only=False):
        # key_gen("root")
        # key_append("root")

        print colored('==========================', 'blue')
        print colored('SYNC: Apache Document Root', 'blue')
        print colored('==========================', 'blue')
        rsync_fab.data_to_server_v2(data_dir, data_dir + 'var-www.2016-09-30-15-00-16.tar.gz',
                                    data_dir + 'var/www/', remote_dir + 'var/www/')

        print colored('=========================', 'blue')
        print colored('SYNC: Apache Config Files', 'blue')
        print colored('=========================', 'blue')
        rsync_fab.data_to_server_v2(data_dir, data_dir + 'etc-httpd.2016-09-30-15-36-19.tar.gz',
                                    data_dir + 'etc/httpd/', remote_dir + 'etc/httpd/')

        print colored('======================', 'blue')
        print colored('SYNC: PHP Config Files', 'blue')
        print colored('======================', 'blue')
        # file_send_oldmod(data_dir + 'php.ini', remote_dir + '/etc/')
        rsync_fab.data_to_server_v2(data_dir, data_dir + 'etc-php.d.2016-09-30-15-36-47.tar.gz',
                                    data_dir + 'etc/php.d/', remote_dir + 'etc/php.d/')
        rsync_fab.data_to_server_v2(data_dir, data_dir + 'usr-include-php.2016-09-30-15-36-48.tar.gz',
                                    data_dir + 'usr/include/php/', remote_dir + 'usr/include/php/')

        print colored('=============================', 'blue')
        print colored('SYNC: Shibboleth Config Files', 'blue')
        print colored('=============================', 'blue')
        rsync_fab.data_to_server_v2(data_dir, data_dir + 'etc-shibboleth.2016-09-30-15-36-51.tar.gz',
                                    data_dir + 'etc/shibboleth/', remote_dir + 'etc/shibboleth/')
        key_fab.remove("root")
