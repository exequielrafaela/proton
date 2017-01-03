# Import Fabric's API module#
import os
from time import strftime, gmtime

from fabric.api import settings
from fabric.decorators import task
from fabric.operations import sudo, local, get
from fabric.state import env
from termcolor import colored

from modules import mysql_fab


@task
def download_data_from_server(data_dir, migrate_dir, tmp_migrate_dir="/tmp/"):
    """
Get data from a remote host passing the local data_dir and the
remote migrate_dir to be actually migrated
fab -R devtest rsync_data_from_server()
    :param data_dir: Directory where the data it's going to be stored
    :param migrate_dir: Directory to get from the remote server
    :param tmp_migrate_dir: Directory to host the compress files to get from the remote server
    """
    with settings(warn_only=False):

        data_dir = data_dir + env.host
        print data_dir

        migrate_dir_dash = migrate_dir.replace("/", "-")
        if migrate_dir_dash.startswith('-') and migrate_dir_dash.endswith('-'):
            migrate_dir_dash = migrate_dir_dash[1:-1]

        print colored('=======================', 'blue')
        print colored('Getting: ' + migrate_dir, 'blue')
        print colored('=======================', 'blue')

        if os.path.isdir(data_dir):
            print colored('####################################', 'blue')
            print colored('##### ' + data_dir + ' exists ######', 'blue')
            print colored('####################################', 'blue')
            try:
                print colored('##########################################', 'blue')
                print colored('####### GETING ' + migrate_dir + ' #######', 'blue')
                print colored('##########################################', 'blue')
                date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
                # tar -czvf /path-to/other/directory/file.tar.gz file
                # Consider tar | rsync // tar | scp // tar | netcat (insecure)
                sudo('tar czvf ' + tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz ' + migrate_dir)
                # local('sudo chmod 757 -R ' + data_dir)
                get(tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz', data_dir, use_sudo=True)
                # local('sudo chmod 755 -R ' + data_dir)
                sudo('rm -rf ' + tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz ')

            except SystemExit:
                print colored('##########################################', 'red')
                print colored('##### FAIL to GET' + migrate_dir + ' #####', 'red')
                print colored('##########################################', 'red')
        else:
            local('mkdir -p ' + data_dir)
            try:
                print colored('#########################', 'blue')
                print colored('####### GETING ' + migrate_dir + ' #######', 'blue')
                print colored('#########################', 'blue')
                date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
                # tar -czvf /path-to/other/directory/file.tar.gz file
                sudo('tar czvf ' + tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz ' + migrate_dir)
                # local('sudo chmod 757 ' + data_dir )
                get(tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz', data_dir, use_sudo=True)
                # local('sudo chmod 755 ' + data_dir)
                sudo('rm -rf ' + tmp_migrate_dir + migrate_dir_dash + '.' + date + '.tar.gz ')

            except SystemExit:
                print colored('#############################################', 'red')
                print colored('##### FAIL to RSYNC ' + migrate_dir + ' #####', 'red')
                print colored('#############################################', 'red')


@task
def download_lamp_from_server(data_dir):
    """
Download LAMP data using download_data_from_server task
    :param data_dir: Directory where the data it's going to be stored in the jumphost
    """
    with settings(warn_only=False):
        print colored('==========================', 'blue')
        print colored('SYNC: Apache Document Root', 'blue')
        print colored('==========================', 'blue')
        download_data_from_server(data_dir, '/var/www/')

        print colored('=========================', 'blue')
        print colored('SYNC: Apache Config Files', 'blue')
        print colored('=========================', 'blue')
        download_data_from_server(data_dir, '/etc/httpd/')

        print colored('======================', 'blue')
        print colored('SYNC: PHP Config Files', 'blue')
        print colored('======================', 'blue')
        # local('sudo chmod 757 ' + data_dir + env.host)
        get('/etc/php.ini', data_dir + env.host, use_sudo=True)
        # local('sudo chmod 755 ' + data_dir + env.host)
        download_data_from_server(data_dir, '/etc/php.d/')
        download_data_from_server(data_dir, '/usr/include/php/')

        print colored('=============================', 'blue')
        print colored('SYNC: Shibboleth Config Files', 'blue')
        print colored('=============================', 'blue')
        download_data_from_server(data_dir, '/etc/shibboleth/')


@task
def download_feeds_from_server(data_dir):
    """
Download LAMP data using download_data_from_server task
    :param data_dir: Directory where the data it's going to be stored in the jumphost
    """
    with settings(warn_only=False):
        print colored('==========================', 'blue')
        print colored('SYNC: Apache Document Root', 'blue')
        print colored('==========================', 'blue')
        download_data_from_server(data_dir, '/var/www/feedsreader/')

    mysql_fab.backup_db("/mnt/resource/172.17.2.30/", "/tmp/", "root", "feedsreader", mysql_ip="127.0.0.1")
