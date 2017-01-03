# Import Fabric's API module#
import os

from fabric.api import settings
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.decorators import task
from fabric.operations import sudo, local, get, put
from termcolor import colored


@task
def rsync(local_dir, remote_dir, exclude, default_opts, extra_opts):
    """
Python fabric rsync
    :param local_dir:
    :param remote_dir:
    :param exclude:
    :param default_opts:
    :param extra_opts:
    """
    with settings(warn_only=False):
        rsync_project(remote_dir, local_dir, exclude, default_opts, extra_opts)


@task
def data_from_server(data_dir="/tmp/"):
    """
Migrate the data from a LAMP Server to a new one mainly using rsync
fab -R devtest rsync_data_from_server()
    :param data_dir: Directory where the rsync data it's going to be stored
    """
    with settings(warn_only=False):
        print colored('===========================', 'blue')
        print colored('SYNC: Apache Document Root', 'blue')
        print colored('===========================', 'blue')

        if os.path.isdir(data_dir + 'var/www'):
            print colored('################################', 'blue')
            print colored('##### ' + data_dir + 'var/www exists ######', 'blue')
            print colored('################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync web root
                # sudo('rsync -avzP --progress /var/www/ apache@172.17.2.30:/var/www/')
                # local: rsync  -avzP --progress  --rsh='ssh  -p 22  ' /tmp/ vagrant@172.28.128.4:/var/www
                rsync_project(local_dir=data_dir + 'var/www/', remote_dir='/var/www/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('##############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Document Root #####', 'red')
                print colored('##############################################', 'red')
        else:
            local('mkdir -p ' + data_dir + 'var/www')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync web root
                # sudo('rsync -avzP --progress /var/www/ apache@172.17.2.30:/var/www/')
                # local: rsync  -avzP --progress  --rsh='ssh  -p 22  ' /tmp/ vagrant@172.28.128.4:/var/www
                rsync_project(local_dir=data_dir + 'var/www/', remote_dir='/var/www/', default_opts='-avzP --progress',
                              upload=False)
            except SystemExit:
                print colored('##############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Document Root #####', 'red')
                print colored('##############################################', 'red')

        print colored('=========================', 'blue')
        print colored('SYNC: Apache Config Files', 'blue')
        print colored('=========================', 'blue')

        if os.path.isdir(data_dir + 'etc/httpd'):
            print colored('##################################', 'blue')
            print colored('##### ' + data_dir + 'etc/httpd exists ######', 'blue')
            print colored('##################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync the apache configuration files
                # sudo('rsync -avzP --progress /etc/httpd/ apache@172.17.2.30:/etc/httpd.old/')
                rsync_project(local_dir=data_dir + 'etc/httpd/', remote_dir='/etc/httpd/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('#############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Config Files #####', 'red')
                print colored('#############################################', 'red')
        else:
            local('mkdir -p ' + data_dir + 'etc/httpd')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync the apache configuration files
                # sudo('rsync -avzP --progress /etc/httpd/ apache@172.17.2.30:/etc/httpd.old/')
                rsync_project(local_dir=data_dir + 'etc/httpd/', remote_dir='/etc/httpd/',
                              default_opts='-avzP --progress',
                              upload=False)
            except SystemExit:
                print colored('#############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Config files #####', 'red')
                print colored('#############################################', 'red')

        print colored('======================', 'blue')
        print colored('SYNC: PHP Config Files', 'blue')
        print colored('======================', 'blue')

        if os.path.isdir(data_dir + "etc/php.d") and os.path.isdir(data_dir + "usr/include/php"):
            print colored('###############################', 'blue')
            print colored('##### PHP folders exists ######', 'blue')
            print colored('###############################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync php configuration
                # comparar memory limit => llevarlo a 512mb o 1gb
                # sudo('scp /etc/php.ini root@172.17.2.30:/etc/php.ini.old/')
                # upload_project(local_dir='/tmp/etc/', remote_dir='/etc/php.ini', use_sudo=True)
                get('/etc/php.ini', data_dir + 'etc/')
                # sudo('rsync -avzP --progress /etc/php.d/ 172.17.2.30:/etc/php.d.old/')
                rsync_project(local_dir=data_dir + 'etc/php.d', remote_dir='/etc/php.d/',
                              default_opts='-avzP --progress', upload=False)
                # sudo('rsync -avzP --progress /usr/include/php/ 172.17.2.30:/usr/include/php.old/')
                rsync_project(local_dir=data_dir + 'usr/include/php/', remote_dir='/usr/include/php/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('##########################################', 'red')
                print colored('##### FAIL to RSYNC PHP Config Files #####', 'red')
                print colored('##########################################', 'red')
        else:
            local('mkdir -p /tmp/etc/php.d')
            local('mkdir -p /tmp/usr/include/php')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync php configuration
                # comparar memory limit => llevarlo a 512mb o 1gb
                # sudo('scp /etc/php.ini root@172.17.2.30:/etc/php.ini.old/')
                # upload_project(local_dir='/tmp/etc/', remote_dir='/etc/php.ini', use_sudo=True)
                get('/etc/php.ini', data_dir + 'etc/')
                # sudo('rsync -avzP --progress /etc/php.d/ 172.17.2.30:/etc/php.d.old/')
                rsync_project(local_dir=data_dir + 'etc/php.d', remote_dir='/etc/php.d/',
                              default_opts='-avzP --progress',
                              upload=False)
                # sudo('rsync -avzP --progress /usr/include/php/ 172.17.2.30:/usr/include/php.old/')
                rsync_project(local_dir=data_dir + 'usr/include/php/', remote_dir='/usr/include/php/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('##########################################', 'red')
                print colored('##### FAIL to RSYNC PHP Config Files #####', 'red')
                print colored('##########################################', 'red')

        """
        print colored('========================', 'blue')
        print colored('SYNC: MySQL Config Files', 'blue')
        print colored('========================', 'blue')

        if (os.path.isdir(data_dir+"etc/mysql")):
            print colored('#################################', 'blue')
            print colored('##### MySQL folders exists ######', 'blue')
            print colored('#################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync mysql config files
                # sudo('rsync -avzP --progress /etc/mysql/ 172.17.2.30:/etc/mysql.old/')
                rsync_project(local_dir=data_dir+'etc/mysql/', remote_dir='/etc/mysql/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('############################################', 'red')
                print colored('##### FAIL to RSYNC MySQL Config Files #####', 'red')
                print colored('############################################', 'red')
        else:
            local('mkdir -p /tmp/etc/mysql')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync mysql config files
                # sudo('rsync -avzP --progress /etc/mysql/ 172.17.2.30:/etc/mysql.old/')
                rsync_project(local_dir=data_dir+'etc/mysql/', remote_dir='/etc/mysql/',
                             default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('############################################', 'red')
                print colored('##### FAIL to RSYNC MySQL Config Files #####', 'red')
                print colored('############################################', 'red')
        """

        print colored('=============================', 'blue')
        print colored('SYNC: Shibboleth Config Files', 'blue')
        print colored('=============================', 'blue')

        if os.path.isdir(data_dir + "etc/shibboleth"):
            print colored('######################################', 'blue')
            print colored('##### Shibboleth folders exists ######', 'blue')
            print colored('######################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync shibboleth config files
                # sudo('rsync -avzP --progress /etc/shibboleth/ 172.17.2.30:/etc/shibboleth.old/')
                rsync_project(local_dir=data_dir + 'etc/shibboleth/', remote_dir='/etc/shibboleth/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('#################################################', 'red')
                print colored('##### FAIL to RSYNC Shibboleth Config Files #####', 'red')
                print colored('#################################################', 'red')
        else:
            local('mkdir -p /tmp/etc/shibboleth')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync shibboleth config files
                # sudo('rsync -avzP --progress /etc/shibboleth/ 172.17.2.30:/etc/shibboleth.old/')
                rsync_project(local_dir=data_dir + 'etc/shibboleth/', remote_dir='/etc/shibboleth/',
                              default_opts='-avzP --progress', upload=False)
            except SystemExit:
                print colored('#################################################', 'red')
                print colored('##### FAIL to RSYNC Shibboleth Config Files #####', 'red')
                print colored('#################################################', 'red')


@task
def data_to_server(data_dir="/tmp/"):
    """
Migrate the data from a Jumphost Server to a new LAMP Server mainly using rsync
fab -R devtest rsync_data_to_server()
    :param data_dir: Directory where the rsync data it's going to be stored
    """
    with settings(warn_only=False):
        print colored('===========================', 'blue')
        print colored('SYNC: Apache Document Root', 'blue')
        print colored('===========================', 'blue')

        if os.path.isdir(data_dir + "var/www"):
            print colored('################################', 'blue')
            print colored('##### /tmp/var/www exists ######', 'blue')
            print colored('################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync web root
                # sudo('rsync -avzP --progress /var/www/ apache@172.17.2.30:/var/www/')
                # local: rsync  -avzP --progress  --rsh='ssh  -p 22  ' /tmp/ vagrant@172.28.128.4:/var/www
                if exists(data_dir + 'var/www', use_sudo=True):
                    rsync_project(local_dir=data_dir + 'var/www/', remote_dir=data_dir + 'var/www/',
                                  default_opts='-avzP --progress')
                else:
                    sudo('mkdir -p ' + data_dir + 'var/www/')
                    rsync_project(local_dir=data_dir + 'var/www/', remote_dir=data_dir + 'var/www/',
                                  default_opts='-avzP --progress')
            except SystemExit:
                print colored('##############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Document Root #####', 'red')
                print colored('##############################################', 'red')
        else:
            print colored('###########################################################', 'red')
            print colored('##### Check that Apache Document Root exists in ' + data_dir + ' #####', 'red')
            print colored('###########################################################', 'red')

        print colored('=========================', 'blue')
        print colored('SYNC: Apache Config Files', 'blue')
        print colored('=========================', 'blue')

        if os.path.isdir(data_dir + "etc/httpd"):
            print colored('##################################', 'blue')
            print colored('##### ' + data_dir + 'etc/httpd exists ######', 'blue')
            print colored('##################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync the apache configuration files
                # sudo('rsync -avzP --progress /etc/httpd/ apache@172.17.2.30:/etc/httpd.old/')
                if exists(data_dir + 'etc/httpd', use_sudo=True):
                    rsync_project(local_dir=data_dir + 'etc/httpd/', remote_dir=data_dir + 'etc/httpd/',
                                  default_opts='-avzP --progress')
                else:
                    sudo('mkdir -p ' + data_dir + 'etc/httpd')
                    rsync_project(local_dir=data_dir + 'etc/httpd/', remote_dir=data_dir + 'etc/httpd/',
                                  default_opts='-avzP --progress')
            except SystemExit:
                print colored('#############################################', 'red')
                print colored('##### FAIL to RSYNC Apache Config Files #####', 'red')
                print colored('#############################################', 'red')
        else:
            print colored('########################################################', 'red')
            print colored('##### Check that Apache conf files exists in ' + data_dir + ' #####', 'red')
            print colored('########################################################', 'red')

        print colored('======================', 'blue')
        print colored('SYNC: PHP Config Files', 'blue')
        print colored('======================', 'blue')

        if os.path.isdir(data_dir + "etc/php.d") and os.path.isdir(data_dir + "usr/include/php"):
            print colored('###############################', 'blue')
            print colored('##### PHP folders exists ######', 'blue')
            print colored('###############################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                if exists(data_dir + 'etc/php.d', use_sudo=True) and exists(data_dir + 'usr/include/php',
                                                                            use_sudo=True):
                    # Rsync php configuration
                    # comparar memory limit => llevarlo a 512mb o 1gb
                    # sudo('scp /etc/php.ini root@172.17.2.30:/etc/php.ini.old/')
                    # upload_project(local_dir='/tmp/etc/', remote_dir='/etc/php.ini', use_sudo=True)
                    put(data_dir + 'etc/php.ini', data_dir + 'etc/php.ini')
                    # sudo('rsync -avzP --progress /etc/php.d/ 172.17.2.30:/etc/php.d.old/')
                    rsync_project(local_dir=data_dir + 'etc/php.d', remote_dir=data_dir + 'etc/php.d/',
                                  default_opts='-avzP --progress')
                    # sudo('rsync -avzP --progress /usr/include/php/ 172.17.2.30:/usr/include/php.old/')
                    rsync_project(local_dir=data_dir + 'usr/include/php/', remote_dir=data_dir + 'usr/include/php/',
                                  default_opts='-avzP --progress')
                else:
                    sudo('mkdir -p ' + data_dir + 'etc/php.d')
                    sudo('mkdir -p ' + data_dir + 'usr/include/php')
                    put(data_dir + 'etc/php.ini', data_dir + 'etc/php.ini')
                    rsync_project(local_dir=data_dir + 'etc/php.d', remote_dir=data_dir + 'etc/php.d/',
                                  default_opts='-avzP --progress')
                    rsync_project(local_dir=data_dir + 'usr/include/php/', remote_dir=data_dir + 'usr/include/php/',
                                  default_opts='-avzP --progress')
            except SystemExit:
                print colored('##########################################', 'red')
                print colored('##### FAIL to RSYNC PHP Config Files #####', 'red')
                print colored('##########################################', 'red')
        else:
            print colored('#####################################################', 'red')
            print colored('##### Check that PHP conf files exists in ' + data_dir + ' #####', 'red')
            print colored('#####################################################', 'red')

        """
        print colored('========================', 'blue')
        print colored('SYNC: MySQL Config Files', 'blue')
        print colored('========================', 'blue')

        if (os.path.isdir(data_dir+"etc/mysql")):
            print colored('#################################', 'blue')
            print colored('##### MySQL folders exists ######', 'blue')
            print colored('#################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync mysql config files
                # sudo('rsync -avzP --progress /etc/mysql/ 172.17.2.30:/etc/mysql.old/')
                rsync_project(local_dir=data_dir+'etc/mysql/', remote_dir='/etc/mysql/',
                              default_opts='-avzP --progress')
            except SystemExit:
                print colored('############################################', 'red')
                print colored('##### FAIL to RSYNC MySQL Config Files #####', 'red')
                print colored('############################################', 'red')
        else:
            local('mkdir -p '+data_dir+'etc/mysql')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                # Rsync mysql config files
                # sudo('rsync -avzP --progress /etc/mysql/ 172.17.2.30:/etc/mysql.old/')
                rsync_project(local_dir=data_dir+'etc/mysql/', remote_dir='/etc/mysql/',
                              default_opts='-avzP --progress')
            except SystemExit:
                print colored('############################################', 'red')
                print colored('##### FAIL to RSYNC MySQL Config Files #####', 'red')
                print colored('############################################', 'red')
        """

        print colored('=============================', 'blue')
        print colored('SYNC: Shibboleth Config Files', 'blue')
        print colored('=============================', 'blue')

        if os.path.isdir(data_dir + "etc/shibboleth"):
            print colored('######################################', 'blue')
            print colored('##### Shibboleth folders exists ######', 'blue')
            print colored('######################################', 'blue')
            try:
                print colored('#########################', 'blue')
                print colored('####### RSYNCKING #######', 'blue')
                print colored('#########################', 'blue')
                if exists(data_dir + 'etc/shibboleth', use_sudo=True):
                    # Rsync shibboleth config files
                    # sudo('rsync -avzP --progress /etc/shibboleth/ 172.17.2.30:/etc/shibboleth.old/')
                    rsync_project(local_dir=data_dir + 'etc/shibboleth/', remote_dir=data_dir + 'etc/shibboleth/',
                                  default_opts='-avzP --progress')
                else:
                    sudo('mkdir -p ' + data_dir + 'etc/shibboleth')
                    rsync_project(local_dir=data_dir + 'etc/shibboleth/', remote_dir=data_dir + 'etc/shibboleth/',
                                  default_opts='-avzP --progress')
            except SystemExit:
                print colored('#################################################', 'red')
                print colored('##### FAIL to RSYNC Shibboleth Config Files #####', 'red')
                print colored('#################################################', 'red')
        else:
            print colored('############################################################', 'red')
            print colored('##### Check that Shibboleth conf files exists in ' + data_dir + ' #####', 'red')
            print colored('############################################################', 'red')


@task
def data_to_server_v2(local_file_dir, local_file_path, local_rsync_dir, remote_dir):
    """
Migrate the data from a Jumphost Server to a new Server mainly using rsync
fab -R devtest rsync_data_to_server_v2()
    :param local_file_dir: Directory where the .tar.gz containing the data to be rsynced w/ the remote host
    :param local_file_path: Absolute path of the .tar.gz containing the data to be rsynced w/ the remote host
    :param local_rsync_dir: Directory where the rsync data it's going to be stored
    :param remote_dir: Remote directory where the rsync data it's going to be stored

eg: fab -R devtest rsync_data_to_server_v2:/tmp/172.28.128.4/,/tmp/172.28.128.4/var-www.2016-09-28-19-11-18.tar.gz,
/tmp/172.28.128.4/var/www/,/tmp/

    """
    with settings(warn_only=False):
        print colored('==============', 'blue')
        print colored('RSYNCING START', 'blue')
        print colored('==============', 'blue')

        if os.path.isfile(local_file_path):
            print colored('###########################################', 'blue')
            print colored('##### ' + local_file_path + ' exists ######', 'blue')
            print colored('###########################################', 'blue')
            try:
                print colored('###############################################', 'blue')
                print colored('####### RSYNCING' + local_file_path + ' #######', 'blue')
                print colored('###############################################', 'blue')
                local('sudo tar xzvf ' + local_file_path + ' -C ' + local_file_dir)
                if os.path.isdir(local_rsync_dir) and exists(remote_dir):
                    rsync_project(local_dir=local_rsync_dir, remote_dir=remote_dir,
                                  default_opts='-avzP --progress')
                    local('sudo find ' + local_file_dir + '* -type d | sudo xargs rm -rf --')
                else:
                    try:
                        sudo('mkdir -p ' + remote_dir)
                        rsync_project(local_dir=local_rsync_dir, remote_dir=remote_dir,
                                      default_opts='-avzP --progress')
                        local('sudo find ' + local_file_dir + '* -type d | sudo xargs rm -rf --')
                        # local('sudo rm -rf ' + local_rsync_dir[:-1])

                    except SystemExit:
                        print colored('#################################################################', 'red')
                        print colored('##### Check that all the DIRS passed as args are consistent #####', 'red')
                        print colored('#################################################################', 'red')
            except SystemExit:
                print colored('###############################', 'red')
                print colored('##### FAIL to RSYNC Files #####', 'red')
                print colored('###############################', 'red')
        else:
            print colored('##########################################################', 'red')
            print colored('##### Check that files ' + local_file_path + 'exists #####', 'red')
            print colored('##########################################################', 'red')
