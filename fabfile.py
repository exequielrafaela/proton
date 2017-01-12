# coding=utf-8

"""
========================================================================
| Fabfile to:                                                           |
|    - AUTOMATE SEVERAL LINUX INFRA TASKS.                              |
|    - to invoke: fab -f file -R role func:arguemnt1,argument2          |
|    - $ fab -f /home/usernamex/fabfile.py -R local gen_key:username    |
|                                                                       |
|    - If the "fabfile.py" is in the current dir then just:             |
|    - $ fab -R dev push_key:username                                   |
|    - $ fab -R dev test_key:username                                   |
|                                                                       |
|    - $ fab show_help for more information                             |
========================================================================
"""

# ORDER THE IMPORTS ALPHABETICALLY and DIVIDE IN 3 SECTIONS
# 1st.standard library modules – e.g. sys, os, getopt, re
# 2nd.third-party library modules (anything installed in Python’s site-packages directory)
# – e.g. mx.DateTime, ZODB, PIL.Image, etc
# 3rd.locally-developed modules

import logging
import config
# import sys
# import os
# import base64
# import re

# Import Fabric's API module#
# from fabric.api import hosts, sudo, settings, hide, env, execute, prompt, run, local, task, put, cd, get
from fabric.api import sudo, settings, env, run, cd
from fabric.colors import red, blue, yellow, green
# from fabric.contrib.files import append, exists, sed
from fabric.contrib.files import exists, sed
from termcolor import colored
# from fabric.contrib.project import rsync_project, upload_project
# from distutils.util import strtobool

# import iptools
# import time
# import ConfigParser
# from optparse import OptionParser
# from time import gmtime, strftime
# from passlib.hash import pbkdf2_sha256

from modules import chef_fab
from modules import conf_files_fab
from modules import download_files_fab
from modules import file_fab
from modules import inst_centos_7_fab
from modules import inst_ubu_14_fab
from modules import key_fab
from modules import logger_fab
from modules import mail_fab
from modules import mysql_fab
from modules import nfs_fab
from modules import passwd_fab
from modules import pkg_mgr_fab
from modules import rm_centos_7_fab
from modules import rsync_fab
from modules import show_fab
from modules import upload_files_fab
from modules import users_fab

print config.CONFIG_DIR

# As a good practice we can log the state of each phase in our script.
#  https://docs.python.org/2.7/howto/logging.html
logging.basicConfig(filename='./logs/check_ssh.log', level=logging.DEBUG)
logging.info('LOG STARTS')
# logging.debug('This message should go to the log file')
# logging.warning('And this, too')

# Open the server list file and split the IP o each server.
with open("./conf/servers/out_users_test.txt", "r") as f:
    ServerList = [line.split()[0] for line in f]

# In env.roledefs we define the remote servers. It can be IP Addrs or domain names.
env.roledefs = {
    'local': ['localhost'],
    'devtest': ServerList
}

# Fabric user and pass.
# env.user = "root"
# env.password = "toor"
# env.key_filename = '/home/username/.ssh/id_rsa'
# env.warn_only=True
env.pararel = True
env.shell = "/bin/sh -c"
env.skip_bad_hosts = True
# env.abort_on_prompts = True
env.timeout = 5


def command(cmd):
    """
Run a command in the host/s
    :param cmd: bash command to be executed
    eg: fab -R dev command:hostname
    """
    with settings(warn_only=False):
        run(cmd)
        print blue('cmd has been run')
        print red('cmd has been run')
        print yellow('cmd has been run')
        print green('cmd has been run')


def haproxy_ws(action, ws_ip):
    """
Add/Remove a WS from a Haproxy Load Balancer
    :param action: "add" or "remove"
    :param ws_ip: Web Server IP Address
    """
    with settings(warn_only=False):
        with cd('/etc/haproxy'):
            try:
                ws_conf = sudo('sudo cat haproxy.cfg | grep "' + ws_ip + ':80 weight 1 check" | head -n1')
                # ws_conf = str(ws_conf.lstrip())
                print colored('=========================================', 'blue')
                print colored('Server ' + ws_ip + ' FOUND in haproxy.cfg', 'blue')
                print colored('=========================================', 'blue')
                print colored(ws_conf, 'cyan', attrs=['bold'])

                if ws_conf == "":
                    print colored('=========================================', 'red')
                    print colored('Server ' + ws_ip + ' NOT FOUND in haproxy.cfg', 'red')
                    print colored('=========================================', 'red')

                elif "disabled" in ws_conf and action == "add":
                    # we erase the last word "disabled" & create the new file add_ws
                    add_ws = ws_conf.rsplit(' ', 1)[0]
                    print colored('=========================================', 'blue')
                    print colored('SERVER ' + ws_ip + ' WILL BE ADDED to the HLB', 'blue')
                    print colored('=========================================', 'blue')
                    print colored('Line to be ADDED:', attrs=['bold'])
                    print colored(add_ws, 'cyan', attrs=['bold'])

                    print colored('Line to be REMOVED:', attrs=['bold'])
                    remove_ws = ws_conf
                    print colored(remove_ws, 'cyan', attrs=['bold'])

                    sudo('chmod 757 /etc/haproxy/')
                    sudo('chmod 606 /etc/haproxy/haproxy.cfg')
                    sed('/etc/haproxy/haproxy.cfg', remove_ws, add_ws, limit='', use_sudo=True, backup='.bak', flags='',
                        shell=False)
                    # fabric.contrib.files.sed(filename, before, after, limit='', use_sudo=False,
                    #  backup='.bak', flags='', shell=False)
                    # sudo('sed -i "/'+remove_ws+'/c\'+add_ws+' haproxy.cfg')
                    sudo('chmod 755 /etc/haproxy/')
                    sudo('chmod 600 /etc/haproxy/haproxy.cfg')

                    sudo('systemctl restart haproxy')

                    print colored('=============================================', 'blue', attrs=['bold'])
                    print colored('SERVER ' + ws_ip + ' SUCCESFULLY ADDED to HLB', 'blue', attrs=['bold'])
                    print colored('=============================================', 'blue', attrs=['bold'])

                elif "disabled" not in ws_conf and action == "remove":
                    add_ws = ws_conf + " disabled"
                    print colored('=================================================', 'blue')
                    print colored('SERVER ' + ws_ip + ' WILL BE REMOVED from the HLB', 'blue')
                    print colored('=================================================', 'blue')
                    print colored('Line to be ADDED:', attrs=['bold'])
                    print colored(add_ws, 'cyan', attrs=['bold'])

                    print colored('Line to be REMOVED:', attrs=['bold'])
                    remove_ws = ws_conf
                    print colored(remove_ws, 'cyan', attrs=['bold'])

                    sudo('chmod 757 /etc/haproxy/')
                    sudo('chmod 606 /etc/haproxy/haproxy.cfg')
                    sed('/etc/haproxy/haproxy.cfg', remove_ws, add_ws, limit='', use_sudo=True, backup='.bak', flags='',
                        shell=False)
                    sudo('chmod 755 /etc/haproxy/')
                    sudo('chmod 600 /etc/haproxy/haproxy.cfg')

                    sudo('systemctl restart haproxy')

                    print colored('================================================', 'blue', attrs=['bold'])
                    print colored('SERVER ' + ws_ip + ' SUCCESFULLY REMOVED from HLB', 'blue', attrs=['bold'])
                    print colored('================================================', 'blue', attrs=['bold'])

                else:
                    print colored('===========================================================================', 'red')
                    print colored('WRONG ARGs or conditions unmets, eg: trying to add a WS that already exists', 'red')
                    print colored('===========================================================================', 'red')
            except SystemExit:
                print colored('=======================================================', 'red')
                print colored('Problem found haproxy.cfg not found - check istallation', 'red')
                print colored('=======================================================', 'red')


def maltrail(role):
    """
Instaling maltrail IDS as Server or Sensor
    :param role: "server" or "sernsor"
    """
    with settings(warn_only=False):
        try:
            # DEPENDENCIAS for AMAZON LINUX:
            # sudo yum install libpcap-devel
            # sudo yum install libnet
            # sudo yum install python-devel
            # sudo yum install gcc-c++
            # sudo yum install git wget
            # wget http://packages.psychotic.ninja/6/base/x86_64/RPMS/schedtool-1.3.0-12.el6.psychotic.x86_64.rpm
            # sudo rpm -Uvh schedtool-1.3.0-12.el6.psychotic.x86_64.rpm
            # wget http://www.coresecurity.com/system/files/pcapy-0.10.6.zip
            # unzip pcapy-0.10.6.zip
            # sudo python setup.py install
            sudo('yum install -y git pcapy schedtool')
            with cd('/home/' + env.user + '/'):
                if exists('/home/' + env.user + '/maltrail', use_sudo=True):
                    print colored('###########################################', 'blue')
                    print colored('####### Directory already created #########', 'blue')
                    print colored('###########################################', 'blue')

                    if role == "sensor":
                        with cd('maltrail'):
                            sudo('python sensor.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    elif role == "server":
                        with cd('/home/' + env.user + '/'):
                            run('[[ -d maltrail ]] || git clone https://github.com/stamparm/maltrail.git')

                        with cd('maltrail/'):
                            sudo('python server.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    else:
                        print colored('=========================================', 'red')
                        print colored('Wrong arg: excects = "sensor" or "server"', 'red')
                        print colored('=========================================', 'red')
                else:
                    print colored('##########################################', 'red')
                    print colored('###### Creating Maltrail Directory #######', 'red')
                    print colored('##########################################', 'red')
                    if role == "sensor":
                        run('git clone https://github.com/stamparm/maltrail.git')
                        with cd('maltrail/'):
                            sudo('python sensor.py ')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')
                            # FOR THE CLIENT #
                            # using configuration file '/home/ebarrirero/maltrail/maltrail.conf.sensor_ok'
                            # using '/var/log/maltrail' for log storage
                            # at least 384MB of free memory required
                            # updating trails (this might take a while)...
                            # loading trails...
                            # 1,135,525 trails loaded

                            # NOTE: #
                            # in case of any problems with packet capture on virtual interface 'any',
                            # please put all monitoring interfaces to promiscuous mode manually
                            #  (e.g. 'sudo ifconfig eth0 promisc')
                            # opening interface 'any'
                            # setting capture filter 'udp or icmp or (tcp and (tcp[tcpflags] == tcp-syn or port 80
                            #  or port 1080 or
                            # port 3128 or port 8000 or port 8080 or port 8118))'
                            # preparing capture buffer...
                            # creating 1 more processes (out of total 2)
                            # please install 'schedtool' for better CPU scheduling
                    elif role == "server":
                        with cd('/home/' + env.user + '/'):
                            run('[[ -d maltrail ]] || git clone https://github.com/stamparm/maltrail.git')
                        with cd('maltrail/'):
                            sudo('python server.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    else:
                        print colored('=========================================', 'red')
                        print colored('Wrong arg: excects = "sensor" or "server"', 'red')
                        print colored('=========================================', 'red')

                        # To stop Sensor and Server instances (if running in background) execute the following:
                        # sudo pkill -f sensor.py
                        # pkill -f server.py

                        # http://127.0.0.1:8338 (default credentials: admin:changeme!)

                        # If option LOG_SERVER is set, then all events are being sent remotely to the Server,
                        # otherwise they are stored directly into the logging directory set with option LOG_DIR,
                        # which can be found inside the maltrail.conf.sensor_ok file's section [All].

                        # In case that the option UPDATE_SERVER is set, then all the trails are being pulled from
                        # the given location, otherwise they are being updated from trails definitions located inside
                        # the installation itself.

                        # Option UDP_ADDRESS contains the server's log collecting listening address
                        # (Note: use 0.0.0.0 to listen on all interfaces), while option UDP_PORT contains
                        # listening port value. If turned on, when used in combination with option LOG_SERVER,
                        # it can be used for distinct (multiple) Sensor <-> Server architecture.

                        # Same as for Sensor, when running the Server (e.g. python server.py) for the first time
                        # and/or after a longer period of non-running, if option
                        #  USE_SERVER_UPDATE_TRAILS is set to true,
                        # it will automatically update the trails from trail definitions (Note: stored inside the
                        # trails directory).
                        # Should server do the trail updates too (to support UPDATE_SERVER)

        except SystemExit:
            print colored('===========================', 'red')
            print colored('Problem installing MALTRAIL', 'red')
            print colored('===========================', 'red')


def disk_usage(tree_dir='/'):
    """
Check a certain folder Disk Usage
    :param tree_dir:
    """
    with settings(warn_only=False):
        import os
        disk = os.statvfs(tree_dir)
        print "preferred file system block size: " + str(disk.f_bsize)
        print "fundamental file system block size: " + str(disk.f_frsize)
        print "total number of blocks in filesystem: " + str(disk.f_blocks)
        print "total number of free blocks: " + str(disk.f_bfree)
        print "free blocks available to non-super user: " + str(disk.f_bavail)
        print "total number of file nodes: " + str(disk.f_files)
        print "total number of free file nodes: " + str(disk.f_ffree)
        print "free nodes available to non-super user: " + str(disk.f_favail)
        print "flags: " + str(disk.f_flag)
        print "miximum file name length: " + str(disk.f_namemax)
        print "~~~~~~~~~~calculation of disk usage:~~~~~~~~~~"
        total_bytes = float(disk.f_frsize * disk.f_blocks)
        print "total space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_bytes, total_bytes / 1024, total_bytes / 1024 / 1024, total_bytes / 1024 / 1024 / 1024)
        total_used_space = float(disk.f_frsize * (disk.f_blocks - disk.f_bfree))
        print "used space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_used_space, total_used_space / 1024, total_used_space / 1024 / 1024,
            total_used_space / 1024 / 1024 / 1024)
        total_avail_space = float(disk.f_frsize * disk.f_bfree)
        print "available space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_avail_space, total_avail_space / 1024, total_avail_space / 1024 / 1024,
            total_avail_space / 1024 / 1024 / 1024)
        total_avail_space_non_root = float(disk.f_frsize * disk.f_bavail)
        print "available space for non-super user: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes " % (
            total_avail_space_non_root, total_avail_space_non_root / 1024, total_avail_space_non_root / 1024 / 1024,
            total_avail_space_non_root / 1024 / 1024 / 1024)


"""
def iptables(action, ip_addr):
    with settings(warn_only=False):
        try:
            print colored('===========================', 'red')
            print colored('IPTABLES START', 'red')
            print colored('===========================', 'red')
        except SystemExit:
            print colored('===========================', 'red')
            print colored('IPTABLES PROBLEM', 'red')
            print colored('===========================', 'red')

            # 62.210.148.246
            # 46.4.116.197
            # 51.254.97.23
            # 171.113.86.129

            # iptables -A INPUT -s <ip> -j DROP
            # iptables -A INPUT -s 62.210.148.246 -j DROP
            # iptables -A INPUT -s 46.4.116.197 -j DROP
            # iptables -A INPUT -s 51.254.97.23 -j DROP
            # iptables -A INPUT -s 171.113.86.129 -j DROP

            # iptables -A INPUT -s 62.24.252.133 -j DROP
            # iptables -A INPUT -s 195.154.187.115 -j DROP
            # iptables -A INPUT -s 176.9.131.69 -j DROP
            # iptables -A INPUT -s 46.165.197.141 -j DROP

            # for ip in list:
            #        iptables -A INPUT
"""

"""
def sp_local(sp_dir):
    with settings(warn_only=False):
        if exists(sp_dir, use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir, 'white', attrs=['bold'])
            with cd(sp_dir):
                try:
                    print colored('#####################################################', 'blue')
                    print colored('####### COMPILE Stream Partitioner w/ MAVEN #########', 'blue')
                    print colored('#####################################################', 'blue')
                    run('mvn install -Dmaven.test.skip=true')
                except:
                    print colored('#############################################################', 'red')
                    print colored('####### FAIL to COMPILE Stream Partitioner w/ MAVEN #########', 'red')
                    print colored('#############################################################', 'red')
        else:
            print colored('###########################################################', 'red')
            print colored('##### Directory /Stream-Partitioner/ does not exists ######', 'red')
            print colored('###########################################################', 'red')

        if exists(sp_dir+'yarara-test/yarara-ace-test/project/', use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir+'yarara-test/yarara-ace-test/project/', 'white', attrs=['bold'])
            with cd(sp_dir+'yarara-test/yarara-ace-test/project/'):
                try:
                    print colored('##################################################', 'blue')
                    print colored('####### RUN Stream Partitioner java -jar #########', 'blue')
                    print colored('##################################################', 'blue')
                    run('cp '+sp_dir+'target/StreamPartitioner-0.0.1-SNAPSHOT.jar SP.jar')
                    run('java -jar SP.jar')
                except:
                    print colored('#########################################################', 'red')
                    print colored('####### FAIL to RUN Stream Partitioner java -jar ########', 'red')
                    print colored('#########################################################', 'red')
        else:
            print colored('################################################', 'red')
            print colored('##### Directory /project/ does not exists ######', 'red')
            print colored('################################################', 'red')

        if exists(sp_dir+'yarara-test/yarara-ace-test/', use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir+'yarara-test/yarara-ace-test/', 'white', attrs=['bold'])
            with cd(sp_dir+'yarara-test/yarara-ace-test/'):
                try:
                    print colored('########################################', 'blue')
                    print colored('####### Creating SP virtual env ########', 'blue')
                    print colored('########################################', 'blue')
                    if exists('create_virtualenv.sh', use_sudo=True):
                        run('chmod +x create_virtualenv.sh')
                        run('./create_virtualenv.sh --http_proxy http://proxy-us.intel.com:911')
                    else:
                        print colored('#############################################', 'red')
                        print colored('#### create_virtualenv.sh does not exist ####', 'red')
                        print colored('#############################################', 'red')

                except:
                    print colored('############################################', 'red')
                    print colored('####### FAIL to Create_virtual env #########', 'red')
                    print colored('############################################', 'red')
        else:
            print colored('############################################################', 'red')
            print colored('##### Dir /yarara-ace-test/ doesnt exists ######', 'red')
            print colored('############################################################', 'red')

        if exists(sp_dir+'yarara-test/yarara-ace-test/', use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir+'yarara-test/yarara-ace-test/', 'white', attrs=['bold'])
            with cd(sp_dir+'yarara-test/yarara-ace-test/'):
                try:
                    if exists('./testFiles', use_sudo=True):
                        print colored('#############################################', 'yellow')
                        print colored('####### testFiles Dir already exists ########', 'yellow')
                        print colored('#############################################', 'yellow')
                    else:
                        print colored('#######################################', 'blue')
                        print colored('####### Creating testFiles Dir ########', 'blue')
                        print colored('#######################################', 'blue')
                        run('mkdir testFiles')

                except:
                    print colored('#############################################', 'red')
                    print colored('####### FAIL to create Dir testFiles ########', 'red')
                    print colored('#############################################', 'red')
        else:
            print colored('############################################################', 'blue')
            print colored('##### Dir /yarara-test-ace/ doesnt exists ######', 'blue')
            print colored('############################################################', 'blue')

        if exists(sp_dir, use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir, 'white', attrs=['bold'])
            with cd(sp_dir):
                try:
                    print colored('########################################################', 'blue')
                    print colored('####### Replacing applications.properties file #########', 'blue')
                    print colored('########################################################', 'blue')
                    run('cp -r -f '+sp_dir+'config/application.properties ./yarara-test/yarara-ace-test/project/config')
                    run('cp -r -f '+sp_dir+'config/application.properties ./yarara-test/yarara-ace-test/config')
                except:
                    print colored('##############################################################', 'red')
                    print colored('####### FAIL to Replace applications.properties file #########', 'red')
                    print colored('##############################################################', 'red')
        else:
            print colored('#########################################################', 'red')
            print colored('#### Directory /Stream-Partitioner/ does not exists #####', 'red')
            print colored('#########################################################', 'red')

        if exists(sp_dir+'yarara-test/yarara-ace-test/', use_sudo=True):
            print colored('##############################', 'blue')
            print colored('##### Directory Tree OK ######', 'blue')
            print colored('##############################', 'blue')
            print colored(sp_dir+'yarara-test/yarara-ace-test/', 'white', attrs=['bold'])
            with cd(sp_dir+'yarara-test/yarara-ace-test/'):
                try:
                    print colored('###############################################', 'blue')
                    print colored('####### Running Yarara component tests ########', 'blue')
                    print colored('###############################################', 'blue')
                    run('chmod +x run_scenarios.sh')
                    run('./run_scenarios.sh -t @COMPONENT --no_proxy NO_PROXY --logging-level DEBUG')

                except:
                    print colored('####################################################', 'red')
                    print colored('####### FAIL to Run Yarara component tests #########', 'red')
                    print colored('####################################################', 'red')
        else:
            print colored('################################################', 'red')
            print colored('##### Dir /yarara-ace-test/ doesnt exists ######', 'red')
            print colored('################################################', 'red')
"""

"""
def push_key(usernamep):
    with settings(warn_only=False):
        #usernamep = prompt("Which USERNAME you like to CREATE & PUSH KEYS?")
        #user_exists = sudo('cat /etc/passwd | grep '+usernamep)
        #user_exists =sudo('grep "^'+usernamep+':" /etc/passwd')
        ##user_exists = sudo('cut -d: -f1 /etc/passwd | grep ' + usernamep)
        #print colored(user_exists, 'green')
        #print(env.host_string)
        #sudo('uname -a')

        try:
        ##if(user_exists != ""):
            user_exists = sudo('cut -d: -f1 /etc/passwd | grep '+usernamep)
            if (user_exists != ""):
                print colored('##############################', 'green')
                print colored('"' + usernamep + '" already exists', 'green')
                print colored('PUSHING KEYS', 'green')
                print colored('##############################', 'green')
                local('sudo chmod 701 /home/' + usernamep)
                local('sudo chmod 741 /home/' + usernamep + '/.ssh')
                local('sudo chmod 604 /home/' + usernamep + '/.ssh/id_rsa')
                local('sudo chmod 604 /home/' + usernamep + '/.ssh/id_rsa.pub')

                local('ssh-copy-id -i /home/' + usernamep + '/.ssh/id_rsa.pub ' + usernamep + '@' + env.host_string)
                sudo('chmod 700 /home/' + usernamep + '/.ssh/authorized_keys')
                sudo('gpasswd -a ' + usernamep + ' wheel')

                local('sudo chmod 700 /home/' + usernamep)
                local('sudo chmod 700 /home/' + usernamep + '/.ssh')
                local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa')
                local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa.pub')
            else:
                print colored('#################################', 'green')
                print colored('"' + usernamep + '" doesnt exists', 'green')
                print colored('PUSHING KEYS', 'green')
                print colored('##################################', 'green')
                local('sudo chmod 701 /home/' + usernamep)
                local('sudo chmod 741 /home/' + usernamep + '/.ssh')
                local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa')
                local('sudo chmod 604 /home/' + usernamep + '/.ssh/id_rsa.pub')

                sudo('useradd ' + usernamep + ' -m -d /home/' + usernamep)
                sudo('echo "' + usernamep + ':' + usernamep + '" | chpasswd')

                # Remember that the usernamep is not in the remote server
                # Then you are gona be ask the pass of this user.
                # To avoid this you must use a user that it's already created
                # in the local and remote host with the proper permissions.
                local('ssh-copy-id -i /home/' + usernamep + '/.ssh/id_rsa.pub ' + usernamep + '@' + env.host_string)
                sudo('chmod 700 /home/' + usernamep + '/.ssh/authorized_keys')
                sudo('gpasswd -a ' + usernamep + ' wheel')

                local('sudo chmod 700 /home/' + usernamep)
                local('sudo chmod 700 /home/' + usernamep + '/.ssh')
                local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa')
                local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa.pub')
        except:
        ##else:
            print colored('#################################', 'green')
            print colored('"' + usernamep + '" doesnt exists', 'green')
            print colored('PUSHING KEYS', 'green')
            print colored('##################################', 'green')
            local('sudo chmod 701 /home/' + usernamep)
            local('sudo chmod 741 /home/' + usernamep + '/.ssh')
            local('sudo chmod 604 /home/' + usernamep + '/.ssh/id_rsa')
            local('sudo chmod 604 /home/' + usernamep + '/.ssh/id_rsa.pub')
            sudo('useradd ' + usernamep + ' -m -d /home/' + usernamep)
            sudo('echo "'+usernamep+':'+usernamep+'" | chpasswd')
            # Remember that the usernamep is not in the remote server
            # Then you are gona be ask the pass of this user.
            # To avoid this you must use a user that it's already created
            # in the local and remote host with the proper permissions.
            local('ssh-copy-id -i /home/'+usernamep+'/.ssh/id_rsa.pub '+usernamep+'@'+env.host_string)
            sudo('chmod 700 /home/'+usernamep+'/.ssh/authorized_keys')
            sudo('gpasswd -a ' + usernamep + ' wheel')
            local('sudo chmod 700 /home/' + usernamep)
            local('sudo chmod 700 /home/' + usernamep + '/.ssh')
            local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa')
            local('sudo chmod 600 /home/' + usernamep + '/.ssh/id_rsa.pub')
"""
