# Import Fabric's API module#
from distutils.util import strtobool

import iptools
from fabric.api import settings
from fabric.contrib.files import exists, run, sudo, cd
from fabric.decorators import task
from termcolor import colored

from modules import file_fab


@task
def nfs_server_centos7(nfs_dir):
    """
Installing NFS Server on a Centos7 host
    :param nfs_dir: NFS Server directory to be shared
    """
    with settings(warn_only=False):
        sudo('yum install -y nfs-utils libnfsidmap libnfsidmap-devel nfs4-acl-tools')

        if exists('/var/' + nfs_dir, use_sudo=True):
            print colored('###########################################', 'blue')
            print colored('####### Directory already created #########', 'blue')
            print colored('###########################################', 'blue')
        else:
            print colored('###########################################', 'red')
            print colored('###### Creating NFS share Directory #######', 'red')
            print colored('###########################################', 'red')
            sudo('mkdir /var/' + nfs_dir)
            sudo('chmod -R 777 /var/' + nfs_dir + '/')
        try:
            # ip_addr = sudo('ifconfig eth0 | awk \'/inet /{print substr($2,1)}\'')
            # netmask = sudo('ifconfig eth0 | awk \'/inet /{print substr($4,1)}\'')
            # subnet_temp = iptools.ipv4.subnet2block(str(ip_addr) + '/' + str(netmask))
            # subnet = subnet_temp[0]
            # sudo('echo "/var/' + nfs_dir + '     ' + subnet + '/' + netmask + '(rw,sync,no_root_squash,no_all_squash)"
            #  > /etc/exports')
            sudo('echo "/var/' + nfs_dir + '     *(rw,sync,no_root_squash)" > /etc/exports')
        except SystemExit:
            # ip_addr = sudo('ifconfig enp0s8 | awk \'/inet /{print substr($2,1)}\'')
            # netmask = sudo('ifconfig enp0s8 | awk \'/inet /{print substr($4,1)}\'')
            # subnet_temp = iptools.ipv4.subnet2block(str(ip_addr) + '/' + str(netmask))
            # subnet = subnet_temp[0]
            # sudo('echo "/var/' + nfs_dir + '     ' + subnet + '/' + netmask + '(rw,sync,no_root_squash,no_all_squash)"
            #  > /etc/exports')
            sudo('echo "/var/' + nfs_dir + '     *(rw,sync,no_root_squash)" > /etc/exports')

        # sudo('sudo exportfs -a')

        sudo('systemctl enable rpcbind')
        sudo('systemctl start rpcbind')

        sudo('systemctl enable nfs-server')
        sudo('systemctl start nfs-server')

        # sudo firewall-cmd --zone=public --add-service=nfs --permanent
        # sudo firewall-cmd --zone=public --add-service=rpc-bind --permanent
        # sudo firewall-cmd --zone=public --add-service=mountd --permanent
        # sudo firewall-cmd --reload


@task
def cachefs_install(nfs_dir, nfs_server_ip, cachedir="/var/cache/fscache", selinux='False'):
    """
cachefilesd (NFS Cache) installation function
fab -R dev cachefs_install:nfsshare,\"172.28.128.3\",mycache-test,/var/cache/fscache-test/
    :param nfs_dir: NFS Server directory
    :param nfs_server_ip: NFS Server IP Address
    :param cachedir: NFS Cache directory
    :param selinux: "False" or "True"

NOTE:
Pending to check code to support "cachetag" argument:
cachetag: Tag to identify the NFS cache in case we have many caches
def cachefs_install(nfs_dir, nfs_server_ip, cachetag="mycache", cachedir="/var/cache/fscache", selinux='False'):
    """
    with settings(warn_only=False):
        # INSTALL FS-CACHE PACKAGE #
        sudo('yum install -y cachefilesd')

        # CHECK IF SELINUX ENFORMENT is ENABLED #
        print colored('=====================================================', 'blue')
        print colored('RELOCATING THE CACHE WITH SELINUX ENFORCEMENT ENABLED', 'blue')
        print colored('=====================================================', 'blue')
        # consider that we are not using this variable for the moment this the code
        # that calls it, it's commented.
        selinux = bool(strtobool(selinux))
        print selinux
        # setenforce enforcing
        # setenforce permissive
        # sestatus
        try:
            selinux_mode = (sudo('sestatus | grep "Current mode:                   enforcing"'))
            if selinux_mode != "":
                selinux = bool(strtobool('True'))
            else:
                selinux = bool(strtobool('False'))
        except SystemExit:
            selinux_mode = (sudo('sestatus | grep "Current mode:                   permissive"'))
            if selinux_mode != "":
                selinux = bool(strtobool('False'))
            else:
                selinux = bool(strtobool('True'))
        # finally:
        #   Peace of code that will be always executed no mater what
        # END OF SELINUX ENFORMENT is ENABLED CHECK #

        # CONFIGURING FS-CACHE SELINUX #
        # We'll use the documentation folder to host them #
        if exists('/etc/cachefilesd.conf', use_sudo=True):
            print colored('#################################', 'yellow')
            print colored('##### CACHEFS conf file OK ######', 'yellow')
            print colored('#################################', 'yellow')

            # ====================
            # RELOCATING THE CACHE
            # ====================
            # By default, the cache is located in /var/cache/fscache, but this may be
            # undesirable.  Unless SELinux is being used in enforcing mode, relocating the
            # cache is trivially a matter of changing the "dir" line in /etc/cachefilesd.

            # However, if SELinux is being used in enforcing mode, then it's not that
            # simple.  The security policy that governs access to the cache must be changed.

            with cd('/usr/share/doc/cachefilesd-*/'):
                if selinux is False:
                    if exists(cachedir, use_sudo=True):
                        print colored('###########################################', 'yellow')
                        print colored('##### Local Cache Dir already exists ######', 'yellow')
                        print colored('###########################################', 'yellow')
                    else:
                        sudo('mkdir ' + cachedir)

                    file_fab.send_mod('/vagrant/scripts/conf/cachefs/cachefilesd.conf', '/etc/cachefilesd.conf', '664')
                    """
                elif(selinux == True):
                    print colored('#######################################', 'red', attrs=['bold'])
                    print colored('########### NOT WORKING YET! ##########', 'red', attrs=['bold'])
                    print colored('#######################################', 'red', attrs=['bold'])

                    # Default policy interface for the CacheFiles userspace management daemon
                    # #/usr/share/selinux/devel/include/contrib/cachefilesd.if
                    sudo('yum install -y checkpolicy selinux-policy*')
                    print colored(sudo('sestatus'), 'cyan', attrs=['bold'])

                    if exists('/usr/share/doc/cachefilesd-*/'+cachetag, use_sudo=True):
                        print colored('##########################################', 'yellow')
                        print colored('##### Conf Cache Dir already exists ######', 'yellow')
                        print colored('##########################################', 'yellow')
                    else:
                        sudo('mkdir '+cachetag)

                    if exists('/usr/share/doc/cachefilesd-*/'+cachetag+'/'+cachetag+'.te', use_sudo=True):
                        print colored('########################################', 'yellow')
                        print colored('##### '+cachetag+'.te file alredy exists', 'yellow')
                        print colored('########################################', 'yellow')
                    else:
                        sudo('touch '+cachetag+'/'+cachetag+'.te')
                        line1='['+cachetag+'.te]'
                        line2='policy_module('+cachetag+',1.0.0)'
                        line3='require { type cachefiles_var_t; }'
                        filename_te = str(cachetag+'/'+cachetag+'.te')
                        append(filename_te, [line1,line2,line3], use_sudo=True, partial=False, escape=True, shell=False)

                    if exists('/usr/share/doc/cachefilesd-*/'+cachetag+'.fc', use_sudo=True):
                        print colored('##########################################', 'yellow')
                        print colored('##### '+cachetag+'.fc file alredy exists'  , 'yellow')
                        print colored('##########################################', 'yellow')
                    else:
                        sudo('touch '+cachetag+'/'+cachetag+'.fc')
                        line1 ='['+cachetag+'.fc]'
                        line2 =cachedir+'(/.*)? gen_context(system_u:object_r:cachefiles_var_t,s0)'
                        filename_te = str(cachetag + '/' + cachetag + '.fc')
                        append(filename_te, [line1, line2], use_sudo=True, partial=False, escape=True, shell=False)

                    with cd('/usr/share/doc/cachefilesd-*/'+cachetag):
                        sudo('make -f /usr/share/selinux/devel/Makefile '+cachetag+'.pp')
                        sudo('semodule -i '+cachetag+'.pp')
                        sudo('semodule -l | grep '+cachetag)

                    if exists(cachedir, use_sudo=True):
                        print colored('###########################################', 'yellow')
                        print colored('##### Local Cache Dir already exists ######', 'yellow')
                        print colored('###########################################', 'yellow')
                        sudo('restorecon ' + cachedir)
                        sudo('ls -dZ ' + cachedir)
                    else:
                        sudo('mkdir '+cachedir)
                        sudo('restorecon '+cachedir)
                        sudo('ls -dZ '+cachedir)

                    # Modify /etc/cachefilesd.conf to point to the correct directory and then
                    # start the cachefilesd service. In our case in /conf/cachefield.conf
                    # config file
                    file_send_mod('/vagrant/scripts/conf/cachefs/cachefilesd.conf', '/etc/cachefilesd.conf', '664')

                    #The auxiliary policy can be later removed by:""
                    #semodule -r '+cachetag+'.pp

                    # If the policy is updated, then the version number in policy_module() in
                    # '+cachetag+'.te should be increased and the module upgraded:
                    # semodule -u '+cachetag+'.pp
                """
                else:
                    print colored('#############################################################################',
                                  'blue')
                    print colored('##### Selinux supported in Permissive mode or when Selinux is disabled ######',
                                  'blue')
                    print colored('#############################################################################',
                                  'blue')

        else:
            print colored('#################################################################', 'red')
            print colored('##### cachefilesd conf does not exists (Check Instalation) ######', 'red')
            print colored('#################################################################', 'red')

        # get status #
        fscachestat = sudo('service cachefilesd status | grep Active | cut -d\' \' -f5')
        parts = fscachestat.split('\n')
        fscachestat = parts[1]

        if fscachestat == "inactive":
            # start it #
            sudo('service cachefilesd start')
            print colored('=================================', 'blue')
            print colored('         FSCACHE STARTED         ', 'blue')
            print colored('=================================', 'blue')
            # Uncoment start it at boot #
            # systemd enable cachefilesd.service
        elif fscachestat == "active":
            # stop it #
            sudo('service cachefilesd restart')
            print colored('=================================', 'blue')
            print colored('        FSCACHE RE-STARTED       ', 'blue')
            print colored('=================================', 'blue')
        else:
            print colored('################################################################', 'red')
            print colored('##### cachefilesd Serv does not exists (Check Instalation) ######', 'red')
            print colored('################################################################', 'red')

        try:
            part_mounted = sudo('df -h | grep /mnt/nfs/var/' + nfs_dir)
            if part_mounted == "":
                # mount nfs client with CacheFS support
                sudo('mount -t nfs -o fsc ' + nfs_server_ip + ':/var/' + nfs_dir + ' /mnt/nfs/var/' + nfs_dir + '/')
            else:
                print colored('##################################################', 'yellow')
                print colored('##### cachefilesd partition already mounted ######', 'yellow')
                print colored('##################################################', 'yellow')
                # sudo('mount -t nfs -o fsc ' + nfs_server_ip + ':/var/' + nfs_dir + ' /mnt/nfs/var/' + nfs_dir + '/')

            sudo('cat /proc/fs/nfsfs/servers')
            sudo('cat /proc/fs/fscache/stats')

        except SystemExit:
            print colored('#########################################', 'red')
            print colored('##### Problem mounting cachefilesd ######', 'red')
            print colored('#########################################', 'red')

        # TESTING #
        print colored('===============================', 'blue')
        print colored('        FILE NOT CACHED        ', 'blue')
        print colored('===============================', 'blue')
        sudo('time cp /mnt/nfs/var/nfsshare/chefdk-0.17.17-1.el7.x86_64.rpm /tmp')

        print colored('==============================', 'blue')
        print colored('        FILE NFS CACHED :)    ', 'blue')
        print colored('==============================', 'blue')
        sudo('time cp /mnt/nfs/var/nfsshare/chefdk-0.17.17-1.el7.x86_64.rpm /dev/null')


@task
def nfs_client_centos7(nfs_dir, nfs_server_ip):
    """
Installing NFS Client for Centos7 system host/s
    :param nfs_dir: NFS Server directory
    :param nfs_server_ip: NFS Server IP Address
    """
    with settings(warn_only=False):
        sudo('yum install -y nfs-utils')
        sudo('mkdir -p /mnt/nfs/var/' + nfs_dir)
        sudo('mount -t nfs ' + nfs_server_ip + ':/var/' + nfs_dir + ' /mnt/nfs/var/' + nfs_dir + '/')
        run('df -kh | grep nfs')
        run('mount | grep nfs')

        try:
            run('touch /mnt/nfs/var/nfsshare/test_nfs')

        except SystemExit:
            print colored('###########################################', 'red')
            print colored('###### NFS client installation Fail #######', 'red')
            print colored('###########################################', 'red')


@task
def nfs_server_centos6(nfs_dir):
    """
Installing NFS Server on a Centos6 host
    :param nfs_dir: NFS Server directory to be shared
    """
    with settings(warn_only=False):
        sudo('yum install -y nfs-utils nfs-utils-lib')

        if exists('/var/' + nfs_dir, use_sudo=True):
            print colored('###########################################', 'blue')
            print colored('####### Directory already created #########', 'blue')
            print colored('###########################################', 'blue')
        else:
            print colored('###########################################', 'red')
            print colored('###### Creating NFS share Directory #######', 'red')
            print colored('###########################################', 'red')
            sudo('mkdir /var/' + nfs_dir)
            sudo('chmod -R 777 /var/' + nfs_dir + '/')

        sudo('chkconfig nfs on')
        sudo('service rpcbind start')
        sudo('service nfs start')

        # ip_addr = sudo('ifconfig eth0 | awk \'/inet /{print substr($2,6)}\'')
        # netmask = sudo('ifconfig eth0 | awk \'/inet /{print substr($4,6)}\'')
        # subnet_temp = iptools.ipv4.subnet2block(str(ip_addr) + '/' + str(netmask))
        # subnet = subnet_temp[0]
        # sudo('echo "/var/' + nfs_dir + '     ' + subnet + '/' + netmask + '(rw,sync,no_root_squash,no_subtree_check)"
        #  > /etc/exports')
        sudo('echo "/var/' + nfs_dir + '     *(rw,sync,no_root_squash)" > /etc/exports')

        sudo('sudo exportfs -a')

        # sudo firewall-cmd --zone=public --add-service=nfs --permanent
        # sudo firewall-cmd --zone=public --add-service=rpc-bind --permanent
        # sudo firewall-cmd --zone=public --add-service=mountd --permanent
        # sudo firewall-cmd --reload


@task
def nfs_client_centos6(nfs_dir, nfs_server_ip):
    """
Installing NFS Client for Centos6 system host/s
    :param nfs_dir: NFS Server directory
    :param nfs_server_ip: NFS Server IP Address
    """
    with settings(warn_only=False):
        sudo('yum install -y nfs-utils nfs-utils-lib')
        sudo('mkdir -p /mnt/nfs/var/' + nfs_dir + '/')
        sudo('mount ' + nfs_server_ip + ':/var/' + nfs_dir + ' /mnt/nfs/var/' + nfs_dir)
        run('df - kh | grep nfs')
        run('mount | grep nfs')

        try:
            run('touch /mnt/nfs/var/nfsshare/test_nfs')

        except SystemExit:
            print colored('###########################################', 'red')
            print colored('###### Check NFS Client configuration #####', 'red')
            print colored('###########################################', 'red')


@task
def nfs_server_ubuntu(nfs_dir):
    """
Install in the host7s NFS Server under Debian/Ubuntu based systems
    :param nfs_dir: NFS directory to be shared
    """
    with settings(warn_only=False):
        sudo('apt-get update')
        sudo('apt-get -y install nfs-kernel-server')

        if exists(nfs_dir, use_sudo=True):
            print colored('###########################################', 'blue')
            print colored('####### Directory already created #########', 'blue')
            print colored('###########################################', 'blue')
        else:
            print colored('###########################################', 'red')
            print colored('###### Creating NFS share Directory #######', 'red')
            print colored('###########################################', 'red')
            sudo('mkdir ' + nfs_dir)
            sudo('chmod -R 777 ' + nfs_dir + '/')
            sudo('chown nobody:nogroup ' + nfs_dir + '/')

        with settings(warn_only=True):
            # sudo('chkconfig nfs on')
            sudo('service rpcbind start')
            sudo('service nfs start')

        ip_addr = sudo('ifconfig eth1 | awk \'/inet /{print substr($2,6)}\'')
        netmask = sudo('ifconfig eth1 | awk \'/inet /{print substr($4,6)}\'')
        subnet_temp = iptools.ipv4.subnet2block(str(ip_addr) + '/' + str(netmask))
        subnet = subnet_temp[0]
        sudo('echo "' + nfs_dir + '     ' + subnet + '/' + netmask +
             '(rw,sync,no_root_squash,no_subtree_check)" > /etc/exports')
        sudo('echo "' + nfs_dir + '     *(rw,sync,no_root_squash)" > /etc/exports')
        sudo('sudo exportfs -a')
        sudo('service nfs-kernel-server start')

        # sudo firewall-cmd --zone=public --add-service=nfs --permanent
        # sudo firewall-cmd --zone=public --add-service=rpc-bind --permanent
        # sudo firewall-cmd --zone=public --add-service=mountd --permanent
        # sudo firewall-cmd --reload
