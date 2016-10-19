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
import sys

"""
ORDER THE IMPORTS ALPHABETICALLY and DIVIDE IN 3 SECTIONS
1st.standard library modules – e.g. sys, os, getopt, re
2nd.third-party library modules (anything installed in Python’s site-packages directory)
 – e.g. mx.DateTime, ZODB, PIL.Image, etc
  3rd.locally-developed modules
"""

# Import Fabric's API module#
# from fabric.api import hosts, sudo, settings, hide, env, execute, prompt, run, local, task, put, cd, get
from fabric.api import sudo, settings, env, run, local, put, cd, get, hide
from fabric.contrib.files import append, exists, sed
from fabric.contrib.project import rsync_project, upload_project
from termcolor import colored
from distutils.util import strtobool
import logging
import os
import base64
import re

# import yum
# import apt
import pwd
import iptools
import getpass
import time
import ConfigParser
from optparse import OptionParser
from time import gmtime, strftime
from passlib.hash import pbkdf2_sha256

import config

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
env.timeout = 5


def show_help():
    """
Show proton help
    cmd: fab show_help
    """
    with settings(warn_only=True):
        print ""
        print "Commands list:"
        print ""
        print "fab show_help                Change behaviour mode to passive"
        print "fab -l                       To list all the fabric functions defined in proton"
        print "fab -d \"task_name\"           To list all the fabric functions defined in proton"
        print "fab show_roles               Change behaviour mode to aggressive"
        print ""
        print "s, q, quit, exit             Exit"


def show_roles():
    """
Show the fabric declared roles
    cmd: fab show_roles
    """
    for key, value in sorted(env.roledefs.items()):
        print key, value


def load_configuration(conf_file, section, option):
    """
    Load configurations from file artemisa.conf
    """
    temp_parser = ""
    with settings(warn_only=False):
        config_parser = ConfigParser.ConfigParser()
        try:
            temp_parser = config_parser.read(conf_file)
            # print temp_parser
        except SystemExit:
            logging.critical("The configuration file artemisa.conf cannot be read.")
        #if temp_parser == []:
            logging.critical("The configuration file artemisa.conf cannot be read.")
            sys.exit(1)
        else:
            try:
                if len(config_parser.sections()) == 0:
                    logging.critical("At least one extension must be defined in extensions.conf.")
                    sys.exit(1)

                # Gets the parameters of mysql
                # self.mysql_section = temp.GetConfigSection(config.CONFIG_SQL_DIR, "mysql")
                # for options in option_list:
                option_value = config_parser.get(section, option)
                # print "Section: " + section + " => " + option + " :" + option_value
                return str(option_value)

            except Exception, e:
                logging.critical(
                    "The configuration file extensions.conf cannot be correctly read. Check it out carefully. "
                    "More info: " + str(e))
                sys.exit(1)


def command(cmd):
    """
Run a command in the host/s
    :param cmd: bash command to be executed
    eg: fab -R dev command:hostname
    """
    with settings(warn_only=False):
        run(cmd)


def file_send(localpath, remotepath):
    """
Send a file to the host/s
    :param localpath: file local path
    :param remotepath: file remote path
    eg: fab -R dev file_send:path/to/edited/ssh_config,/etc/ssh/ssh_config
    # or if the modified ssh_config is in the directory where you’re running Fabric:
    eg: fab file_send:ssh_config,/etc/ssh/ssh_config
    """
    with settings(warn_only=False):
        put(localpath, remotepath, use_sudo=True)


def file_send_mod(localpath, remotepath, modep):
    """
Send a file to the host/s specifying it's permissions
    :param localpath: file local path
    :param remotepath: file remote path
    :param modep:
    eg: fab -R dev file_send_mod:path/to/edited/ssh_config,/etc/ssh/ssh_config,0755
    """
    with settings(warn_only=False):
        put(localpath, remotepath, mode=modep, use_sudo=True)


def file_send_oldmod(localpath, remotepath):
    """
Send a file to the host/s mirroring local permissions
    :param localpath: file local path
    :param remotepath: file remote path
    eg: fab -R dev file_send_oldmod:path/to/edited/ssh_config,/etc/ssh/ssh_config
    """
    with settings(warn_only=False):
        put(localpath, remotepath, mirror_local_mode=True, use_sudo=True)


def file_get(remotepath, localpath):
    """
Retrievng a file from the host/s
    :param remotepath: file remote path
    :param localpath: file local path
    eg: fab -R dev get_file:/var/log/auth.log,/tmp/auth.log
    """
    with settings(warn_only=False):
        get(remotepath, localpath + "." + env.host)


def sudo_command(cmd):
    """
Run a certain command with sudo priviledges
    :param cmd: bash command to be executed as sudo
    #eg : fab -R dev sudo_command:"apt-get install geany"
    """
    with settings(warn_only=False):
        sudo(cmd)


def sudoers_group():
    """
Modify /etc/sudoers adding sudo NOPASSWD wheel group (Still Incomplete)
    """
    with settings(warn_only=False):
        sudo('echo "%wheel        ALL=(ALL)       NOPASSWD: ALL" | (EDITOR="tee -a" visudo)')


def apt_package(action, package):
    """
Install/Upgrade an Debian apt based linux package
    :param action: "install" or "upgrade"
    :param package: name of the package to install
    """
    import apt
    with settings(warn_only=False):
        hostvm = sudo('hostname')
        if action == "install":
            aptcache = apt.Cache()
            if aptcache[package].is_installed:
                print colored('###############################################################################',
                              'yellow')
                print colored(package + ' ALREADY INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'yellow')
                print colored('###############################################################################',
                              'yellow')
            else:
                print colored('###############################################################################', 'blue')
                print colored(package + ' WILL BE INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'blue')
                print colored('###############################################################################', 'blue')
                sudo('apt-get update')
                sudo('apt-get install ' + package)
                aptcachenew = apt.Cache()
                if aptcachenew[package].is_installed:
                    print colored('##################################################################################',
                                  'green')
                    print colored(package + 'SUCCESFULLY INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'green')
                    print colored('##################################################################################',
                                  'green')
                else:
                    print colored('#################################################################################',
                                  'red')
                    print colored(package + 'INSTALLATION PROBLEM in:' + hostvm + '- IP:' + env.host_string, 'red')
                    print colored('#################################################################################',
                                  'red')

        elif action == "upgrade":
            aptcache = apt.Cache()
            if aptcache[package].is_installed:
                print colored('############################################################################', 'yellow')
                print colored(package + ' TO BE UPGRADED in:' + hostvm + '- IP:' + env.host_string, 'yellow')
                print colored('############################################################################', 'yellow')
                sudo('apt-get update')
                sudo('apt-get install --only-upgrade ' + package)
            else:
                print colored('###########################################################################', 'red')
                print colored(package + ' NOT INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'red')
                print colored('###########################################################################', 'red')

        else:
            print colored('############################################################################', 'yellow')
            print colored('Usage eg1: $ fab -R dev apt_package:install,cron', 'red')
            print colored('Usage eg2: $ fab -R dev apt_package:upgrade,gcc', 'red')
            print colored('############################################################################', 'blue')


def yum_package(action, package):
    """
Install/Upgrade an RedHat/Centos yum based linux package
    :param action: "install" or "upgrade"
    :param package: name of the package to install
    """
    with settings(warn_only=False):
        hostvm = sudo('hostname')
        if action == "install":
            # yumcache = yum.YumBase()
            # print(yumcache.rpmdb.searchNevra(name=package))
            try:
                package_inst = sudo('yum list install ' + package)
                print(package_inst)
                # if yumcache.rpmdb.searchNevra(name=package):
                # if not package_inst:
                if package_inst == "":
                    print colored('###############################################################################',
                                  'blue')
                    print colored(package + ' WILL BE INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'blue')
                    print colored('###############################################################################',
                                  'blue')
                    try:
                        sudo('yum install -y ' + package)
                        # yumcache = yum.YumBase()
                        # if yumcache.rpmdb.searchNevra(name=package):
                        package_inst = sudo('yum list install ' + package)
                        if package_inst == "":
                            print colored(
                                '#################################################################################',
                                'red')
                            print colored(package + ' INSTALLATION PROBLEM in:' + hostvm + '- IP:' + env.host_string,
                                          'red')
                            print colored(
                                '#################################################################################',
                                'red')
                        else:
                            print colored(
                                '##################################################################################',
                                'green')
                            print colored(package + ' SUCCESFULLY INSTALLED in:' + hostvm + '- IP:' + env.host_string,
                                          'green')
                            print colored(
                                '##################################################################################',
                                'green')
                    except SystemExit:
                        print colored(
                            '#################################################################################', 'red')
                        print colored(package + ' INSTALLATION PROBLEM in:' + hostvm + '- IP:' + env.host_string, 'red')
                        print colored(
                            '#################################################################################', 'red')
                else:
                    print colored('###############################################################################',
                                  'yellow')
                    print colored(package + ' ALREADY INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'yellow')
                    print colored('###############################################################################',
                                  'yellow')
            except SystemExit:
                print colored('#################################################################################',
                              'red')
                print colored(package + ' INSTALLATION PROBLEM in:' + hostvm + '- IP:' + env.host_string, 'red')
                print colored('#################################################################################',
                              'red')

        elif action == "upgrade":
            # yumcache = yum.YumBase()
            # print(yumcache.rpmdb.searchNevra(name=package))
            # if yumcache.rpmdb.searchNevra(name=package):
            try:
                package_inst = sudo('yum list install ' + package)
                print(package_inst)
                if package_inst == "":
                    print colored('###########################################################################', 'red')
                    print colored(package + ' NOT INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'red')
                    print colored('###########################################################################', 'red')
                else:
                    print colored('############################################################################',
                                  'yellow')
                    print colored(package + ' TO BE UPGRADED in:' + hostvm + '- IP:' + env.host_string, 'yellow')
                    print colored('############################################################################',
                                  'yellow')
                    sudo('yum update -y ' + package)
            except SystemExit:
                print colored('###########################################################################', 'red')
                print colored(package + ' NOT INSTALLED in:' + hostvm + '- IP:' + env.host_string, 'red')
                print colored('###########################################################################', 'red')

        else:
            print colored('############################################################################', 'yellow')
            print colored('Usage eg1: $ fab -R dev yum_package:install,cron', 'red')
            print colored('Usage eg2: $ fab -R dev yum_package:upgrade,gcc', 'red')
            print colored('############################################################################', 'blue')


def user_add_centos(usernamec):
    """
Add a user in RedHat/Centos based OS
    :param usernamec: "username" to add
    """
    with settings(warn_only=True):
        # usernamep = prompt("Which USERNAME you like to CREATE & PUSH KEYS?")
        # user_exists = sudo('cat /etc/passwd | grep '+usernamep)
        # user_exists =sudo('grep "^'+usernamep+':" /etc/passwd')
        # #user_exists = sudo('cut -d: -f1 /etc/passwd | grep ' + usernamep)
        # print colored(user_exists, 'green')
        # print(env.host_string)
        # sudo('uname -a')

        try:
            # if(user_exists != ""):
            user_true = sudo('cut -d: -f1 /etc/passwd | grep ' + usernamec)
            if user_true != "":
                print colored('##############################', 'green')
                print colored('"' + usernamec + '" already exists', 'green')
                print colored('##############################', 'green')
                sudo('gpasswd -a ' + usernamec + ' wheel')
            else:
                print colored('#################################', 'green')
                print colored('"' + usernamec + '" doesnt exists', 'green')
                print colored('WILL BE CREATED', 'green')
                print colored('##################################', 'green')
                sudo('useradd ' + usernamec + ' -m -d /home/' + usernamec)
                # sudo('echo "' + usernamec + ':' + usernamec + '" | chpasswd')
                sudo('gpasswd -a ' + usernamec + ' wheel')
        except SystemExit:
            # else:
            print colored('######################################################', 'green')
            print colored('"' + usernamec + '" couldnt be created for some reason', 'green')
            print colored('######################################################', 'green')


def user_add_ubuntu(usernamec):
    """
Add a user in Debian/Ubuntu based OS
    :param usernamec: "username" to add
    """
    with settings(warn_only=True):
        try:
            # if(user_exists != ""):
            user_true = sudo('cut -d: -f1 /etc/passwd | grep ' + usernamec)
            if user_true != "":
                print colored('##############################', 'green')
                print colored('"' + usernamec + '" already exists', 'green')
                print colored('##############################', 'green')
                # sudo('gpasswd -a ' + usernamec + ' wheel')
            else:
                print colored('#################################', 'green')
                print colored('"' + usernamec + '" doesnt exists', 'green')
                print colored('WILL BE CREATED', 'green')
                print colored('##################################', 'green')
                sudo('useradd ' + usernamec + ' -m -d /home/' + usernamec)
                # sudo('echo "' + usernamec + ':' + usernamec + '" | chpasswd')
                # sudo('gpasswd -a ' + usernamec + ' wheel')
        except SystemExit:
            # else:
            print colored('######################################################', 'green')
            print colored('"' + usernamec + '" couldnt be created for some reason', 'green')
            print colored('######################################################', 'green')


def change_pass(usernameu, upass):
    """
Change RedHat/Centos based OS user password
    :param usernameu: "username" to change password
    :param upass: "password" to be used
    """
    with settings(warn_only=False):
        try:
            # if(user_exists != ""):
            user_true = sudo('cut -d: -f1 /etc/passwd | grep ' + usernameu)
            if user_true != "":
                print colored('#######################################', 'green')
                print colored('"' + usernameu + '" PASSWORD will be changed', 'green')
                print colored('#######################################', 'green')
                sudo('echo ' + usernameu + ':' + upass + ' | chpasswd')
            else:
                print colored('#################################', 'red')
                print colored('"' + usernameu + '" doesnt exists', 'red')
                print colored('#################################', 'red')
        except SystemExit:
            print colored('#################################', 'red')
            print colored('"' + usernameu + '" doesnt exists', 'red')
            print colored('##################################', 'red')


def key_gen(usernameg):
    """
Generate an SSH key for a certain user
Remember that this task it's intended to be run with role "local"
    :param usernameg: "username" to change password
    """
    # global user_exists
    with settings(warn_only=False):
        # usernameg = prompt("Which USERNAME you like to GEN KEYS?")
        # user_exists = sudo('cut -d: -f1 /etc/passwd | grep '+usernameg)
        # user_exists = sudo('cat /etc/passwd | grep ' + usernameg)
        # user_exists = ""
        try:
            user_struct = pwd.getpwnam(usernameg)
            user_exists = user_struct.pw_gecos.split(",")[0]
            print colored(user_exists, 'green')
            if user_exists == "root":
                print colored('#################################################################', 'yellow')
                print colored('CAREFULL: ROOT ssh keys will be generated if they does not exists', 'yellow')
                print colored('#################################################################', 'yellow')
                if os.path.exists('/' + usernameg + '/.ssh/id_rsa'):
                    print colored(str(os.path.exists('/' + usernameg + '/.ssh/id_rsa')), 'blue')
                    print colored('###########################################', 'blue')
                    print colored('username: ' + usernameg + ' KEYS already EXISTS', 'blue')
                    print colored('###########################################', 'blue')
                else:
                    print colored('###########################################', 'blue')
                    print colored('username: ' + usernameg + ' Creating KEYS', 'blue')
                    print colored('###########################################', 'blue')
                    sudo("ssh-keygen -t rsa -f /" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
                    # http://unix.stackexchange.com/questions/36540/why-am-i-still-getting-a-password-prompt-with-ssh
                    # -with-public-key-authentication
                    # sudo('chmod 700 /home/' + usernameg)
                    sudo('chmod 755 /' + usernameg)
                    sudo('chmod 755 /' + usernameg + '/.ssh')
                    sudo('chmod 600 /' + usernameg + '/.ssh/id_rsa')

            elif os.path.exists('/home/' + usernameg + '/.ssh/id_rsa'):
                print colored(str(os.path.exists('/home/' + usernameg + '/.ssh/id_rsa')), 'blue')
                print colored('###########################################', 'blue')
                print colored('username: ' + usernameg + ' KEYS already EXISTS', 'blue')
                print colored('###########################################', 'blue')
            else:
                print colored('###########################################', 'blue')
                print colored('username: ' + usernameg + ' Creating KEYS', 'blue')
                print colored('###########################################', 'blue')
                sudo("ssh-keygen -t rsa -f /home/" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
                # http://unix.stackexchange.com/questions/36540/why-am-i-still-getting-a-password-prompt-with-ssh
                # -with-public-key-authentication
                # sudo('chmod 700 /home/' + usernameg)
                sudo('chmod 755 /home/' + usernameg)
                sudo('chmod 755 /home/' + usernameg + '/.ssh')
                sudo('chmod 600 /home/' + usernameg + '/.ssh/id_rsa')
                sudo('gpasswd -a ' + usernameg + ' wheel')
        except KeyError:
            print colored('####################################', 'blue')
            print colored('User ' + usernameg + 'does not exists', 'blue')
            print colored('####################################', 'blue')

            # if user_exists == "" and usernameg != "root":
            #     print colored('User ' + usernameg + ' does not exist', 'red')
            #     print colored('#######################################################', 'blue')
            #     print colored('Consider that we generate user: username pass: username', 'blue')
            #     print colored('#######################################################', 'blue')
            #
            #     sudo('useradd ' + usernameg + ' -m -d /home/' + usernameg)
            #     sudo('echo "' + usernameg + ':' + usernameg + '" | chpasswd')
            #     sudo("ssh-keygen -t rsa -f /home/" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
            #     sudo('chmod 755 /home/' + usernameg)
            #     sudo('chmod 755 /home/' + usernameg + '/.ssh')
            #     sudo('chmod 600 /home/' + usernameg + '/.ssh/id_rsa')
            #     sudo('gpasswd -a ' + usernameg + ' wheel')


def key_read_file(key_file, username):
    """
In the localhost read and return as a string the public ssh key file given as parameter

    :param key_file: absolute path of the public ssh key
    :param username: username that owns the ssh key
    :return: The public key string
    """
    with settings(warn_only=False):
        key_file = os.path.expanduser(key_file)
        if username == "root":
            if not key_file.endswith('pub'):
                raise RuntimeWarning('Trying to push non-public part of key pair')
            local('sudo chmod 701 /' + username)
            local('sudo chmod 741 /' + username + '/.ssh')
            local('sudo chmod 604 /' + username + '/.ssh/id_rsa.pub')
            with open(key_file) as pyfile:
                return pyfile.read()
        else:
            if not key_file.endswith('pub'):
                raise RuntimeWarning('Trying to push non-public part of key pair')
            with open(key_file) as pyfile:
                return pyfile.read()


def key_append(usernamea):
    """
Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    :param usernamea: "username" to append the key to.
    """
    with settings(warn_only=False):
        if usernamea == "root":
            key_file = '/' + usernamea + '/.ssh/id_rsa.pub'
            key_text = key_read_file(key_file, usernamea)
            if exists('/' + usernamea + '/.ssh/authorized_keys', use_sudo=True):
                local('sudo chmod 701 /' + usernamea)
                local('sudo chmod 741 /' + usernamea + '/.ssh')
                local('sudo chmod 604 /' + usernamea + '/.ssh/id_rsa.pub')
                print colored('#########################################', 'blue')
                print colored('##### authorized_keys file exists #######', 'blue')
                print colored('#########################################', 'blue')
                append('/' + usernamea + '/.ssh/authorized_keys', key_text, use_sudo=True)
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /' + usernamea + '/.ssh/')
                local('sudo chmod 700 /' + usernamea)
                local('sudo chmod 700 /' + usernamea + '/.ssh')
                local('sudo chmod 600 /' + usernamea + '/.ssh/id_rsa.pub')
            else:
                sudo('mkdir -p /' + usernamea + '/.ssh/')
                sudo('touch /' + usernamea + '/.ssh/authorized_keys')
                append('/' + usernamea + '/.ssh/authorized_keys', key_text, use_sudo=True)
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /' + usernamea + '/.ssh/')
                # put('/home/'+usernamea+'/.ssh/authorized_keys', '/home/'+usernamea+'/.ssh/')
                local('sudo chmod 700 /' + usernamea)
                local('sudo chmod 700 /' + usernamea + '/.ssh')
                local('sudo chmod 600 /' + usernamea + '/.ssh/id_rsa.pub')

        else:
            key_file = '/home/' + usernamea + '/.ssh/id_rsa.pub'
            local('sudo chmod 701 /home/' + usernamea)
            local('sudo chmod 741 /home/' + usernamea + '/.ssh')
            local('sudo chmod 604 /home/' + usernamea + '/.ssh/id_rsa.pub')
            key_text = key_read_file(key_file, usernamea)
            local('sudo chmod 700 /home/' + usernamea)
            local('sudo chmod 700 /home/' + usernamea + '/.ssh')
            local('sudo chmod 600 /home/' + usernamea + '/.ssh/id_rsa.pub')
            if exists('/home/' + usernamea + '/.ssh/authorized_keys', use_sudo=True):
                print colored('#########################################', 'blue')
                print colored('##### authorized_keys file exists #######', 'blue')
                print colored('#########################################', 'blue')
                append('/home/' + usernamea + '/.ssh/authorized_keys', key_text, use_sudo=True)
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /home/' + usernamea + '/.ssh/')
            else:
                sudo('mkdir -p /home/' + usernamea + '/.ssh/')
                sudo('touch /home/' + usernamea + '/.ssh/authorized_keys')
                append('/home/' + usernamea + '/.ssh/authorized_keys', key_text, use_sudo=True)
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /home/' + usernamea + '/.ssh/')
                # put('/home/'+usernamea+'/.ssh/authorized_keys', '/home/'+usernamea+'/.ssh/')


def key_remove(usernamea):
    """
Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    :param usernamea: "username" to append the key to.
    """
    with settings(warn_only=False):
        if usernamea == "root":
            key_file = '/' + usernamea + '/.ssh/id_rsa.pub'
            key_text = key_read_file(key_file, usernamea)
            key_text = key_text.rstrip()
            if exists('/' + usernamea + '/.ssh/authorized_keys', use_sudo=True):
                local('sudo chmod 701 /' + usernamea)
                local('sudo chmod 741 /' + usernamea + '/.ssh')
                local('sudo chmod 604 /' + usernamea + '/.ssh/id_rsa.pub')
                print colored('#########################################', 'blue')
                print colored('##### authorized_keys file exists #######', 'blue')
                print colored('#########################################', 'blue')
                key_text = key_text.replace("/", "\/")
                sudo('sed -i -e \'s/' + key_text + '//g\' /' + usernamea + '/.ssh/authorized_keys')
                # sed('/' + usernamea + '/.ssh/authorized_keys', key_text, key_clean,
                #    limit='', use_sudo=True, backup='.bak', flags='', shell=False)
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /' + usernamea + '/.ssh/')
                local('sudo chmod 700 /' + usernamea)
                local('sudo chmod 700 /' + usernamea + '/.ssh')
                local('sudo chmod 600 /' + usernamea + '/.ssh/id_rsa.pub')
            else:
                print colored('#######################################################################################',
                              'yellow')
                print colored(
                    '##### ' + usernamea + ' authorized_keys server:' + env.host + ' file does NOT exists ######',
                    'yellow')
                print colored('#######################################################################################',
                              'yellow')

        else:
            key_file = '/home/' + usernamea + '/.ssh/id_rsa.pub'
            local('sudo chmod 701 /home/' + usernamea)
            local('sudo chmod 741 /home/' + usernamea + '/.ssh')
            local('sudo chmod 604 /home/' + usernamea + '/.ssh/id_rsa.pub')
            key_text = key_read_file(key_file, usernamea)
            local('sudo chmod 700 /home/' + usernamea)
            local('sudo chmod 700 /home/' + usernamea + '/.ssh')
            local('sudo chmod 600 /home/' + usernamea + '/.ssh/id_rsa.pub')
            if exists('/home/' + usernamea + '/.ssh/authorized_keys', use_sudo=True):
                print colored('#########################################', 'blue')
                print colored('##### authorized_keys file exists #######', 'blue')
                print colored('#########################################', 'blue')
                key_text = key_text.rstrip()
                key_text = key_text.replace("/", "\/")
                sudo('sed -i -e \'s/' + key_text + '//g\' /home/' + usernamea + '/.ssh/authorized_keys')
                sudo('chown -R ' + usernamea + ':' + usernamea + ' /home/' + usernamea + '/.ssh/')
            else:
                print colored('#######################################################################################',
                              'yellow')
                print colored(
                    '##### ' + usernamea + ' authorized_keys server:' + env.host + ' file does NOT exists ######',
                    'yellow')
                print colored('#######################################################################################',
                              'yellow')


def key_test(usernamet):
    """
Test SSH (authorized_keys) in the host
    :param usernamet: "username" keys to test
    """
    with settings(warn_only=False):
        # TAKE THE HOME DIR FROM /ETC/PASSWD
        hostvm = sudo('hostname')
        local('sudo chmod 701 /home/' + usernamet)
        local('sudo chmod 741 /home/' + usernamet + '/.ssh')
        local_user = getpass.getuser()
        if os.path.exists('/home/' + local_user + '/temp/'):
            print colored('##################################', 'blue')
            print colored('##### Directory Exists ###########', 'blue')
            print colored('##################################', 'blue')
        else:
            local('mkdir ~/temp')

        local('sudo cp /home/' + usernamet + '/.ssh/id_rsa ~/temp/id_rsa')
        local('sudo chown -R ' + local_user + ':' + local_user + ' ~/temp/id_rsa')
        local('chmod 600 ~/temp/id_rsa')
        # local('sudo chmod 604 /home/' + usernamet + '/.ssh/id_rsa')

        # FIX DONE! - Must copy the key temporaly with the proper permissions
        # in the home directory of the current user executing fabric to use it.
        # Temporally we comment the line 379 and the script must be run by
        # user that desires to test it keys
        # [ntorres@jumphost fabric]$ ssh -i /home/ntorres/.ssh/id_rsa ntorres@10.0.3.113   Warning: Permanently added
        #  '10.0.3.113' (ECDSA) to the list of known hosts.
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # Permissions 0604 for '/home/ntorres/.ssh/id_rsa' are too open.
        # It is required that your private key files are NOT accessible by others.
        # This private key will be ignored.
        # bad permissions: ignore key: /home/ntorres/.ssh/id_rsa
        # Permission denied (publickey).
        # NOTE:
        # there is no way to bypass the keyfile permission check with ssh or ssh-add
        # (and you can't trick it with named pipe or such). Besides, you do not actually want to trick ssh,' \
        # ' but just to be able to use your key files.

        if os.path.exists('/home/' + usernamet + '/.ssh/'):
            ssh_test = local(
                'ssh -i ~/temp/id_rsa -o "StrictHostKeyChecking no" -q ' + usernamet + '@' + env.host_string + ' exit')
            if ssh_test.succeeded:
                print colored('###################################################', 'blue')
                print colored(usernamet + ' WORKED! in:' + hostvm + ' IP:' + env.host_string, 'blue')
                print colored('###################################################', 'blue')
                local('sudo chmod 700 /home/' + usernamet)
                local('sudo chmod 700 /home/' + usernamet + '/.ssh')
                # local('sudo chmod 600 /home/'+usernamet+'/.ssh/id_rsa')
                local('sudo rm ~/temp/id_rsa')
        else:
            print colored('###################################################', 'red')
            print colored(usernamet + ' FAIL! in:' + hostvm + '- IP:' + env.host_string, 'red')
            print colored('###################################################', 'red')


def ruby_install_centos():
    """
Install ruby via rvm in Centos based system
    """
    with settings(warn_only=False):
        # sudo('yum ruby ruby-devel rubygems')
        # yum groupinstall -y development
        # yum groupinstall -y 'development tools'
        sudo('yum groupinstall "Development Tools"')
        sudo('yum install -y git-core zlib zlib-devel gcc-c++ patch readline readline-devel')
        sudo('yum install -y libyaml-devel libffi-devel openssl-devel make bzip2 autoconf automake libtool'
             ' bison curl sqlite-devel')

        # with cd('/home/'+usernamei+'/'):
        with cd('~'):
            run('gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3')
            run('\curl -sSL https://get.rvm.io | bash -s stable --ruby')
            run('source ~/.rvm/scripts/rvm')
            run('gem install bundler')


def knifezero_install_centos():
    """
Install knife zero on RedHat/Centos OS
    """
    with settings(warn_only=False):
        if exists('/tmp/chefdk-0.17.17-1.el7.x86_64.rpm', use_sudo=True):
            print colored('###################################################', 'blue')
            print colored('##### Chef Development Kit already installed ######', 'blue')
            print colored('####################################################', 'blue')
        else:
            print colored('######################################################', 'red')
            print colored('###### Chef Development Kit will be installed  #######', 'red')
            print colored('######################################################', 'red')
            run('wget -P /tmp/ https://packages.chef.io/stable/el/7/chefdk-0.17.17-1.el7.x86_64.rpm')
            sudo('rpm -Uvh /tmp/chefdk-0.17.17-1.el7.x86_64.rpm')

        try:
            knifezero_inst = run('chef gem list | grep knife-zero')
            if knifezero_inst == "":
                run('chef gem install knife-zero')
            else:
                print colored('##############################################', 'blue')
                print colored('##### knife-zero already installed ###########', 'blue')
                print colored('##############################################', 'blue')

            if exists('/opt/chefdk/embedded/bin/knife', use_sudo=True):
                print colored('###########################################', 'blue')
                print colored('##### Knife-zero correctly installed ######', 'blue')
                print colored('###########################################', 'blue')
            else:
                print colored('###########################################', 'red')
                print colored('###### Check chef-zero installation #######', 'red')
                print colored('###########################################', 'red')
        except SystemExit:
            run('chef gem install knife-zero')
            if exists('/opt/chefdk/embedded/bin/knife', use_sudo=True):
                print colored('###########################################', 'blue')
                print colored('##### Knife-zero correctly installed ######', 'blue')
                print colored('###########################################', 'blue')
            else:
                print colored('###########################################', 'red')
                print colored('###### Check chef-zero installation #######', 'red')
                print colored('###########################################', 'red')


def knifezero_conf_centos(usernamek, envs_list=None):
    """
Initialize knife zero on RedHat/Centos OS
    :param usernamek: chef admin user, must have permisses in all the remote servers
    :param envs_list: list with the desired chef environments
    """
    if envs_list is None:
        envs_list = []
    with settings(warn_only=False):
        if exists('/home/' + usernamek + '/my_chef_repo', use_sudo=True):
            print colored('#########################################', 'blue')
            print colored('##### Chef repo dir already exists ######', 'blue')
            print colored('#########################################', 'blue')
        else:
            print colored('################################################', 'red')
            print colored('###### Dir my_chef_repo will be created  #######', 'red')
            print colored('################################################', 'red')
            run('mkdir /home/' + usernamek + '/my_chef_repo')

        if exists('/home/' + usernamek + '/my_chef_repo/knife.rb', use_sudo=True):
            print colored('#########################################', 'blue')
            print colored('##### knife.rb conf already exists ######', 'blue')
            print colored('#########################################', 'blue')
        else:
            print colored('#############################################', 'red')
            print colored('###### knife.rb conf will be created  #######', 'red')
            print colored('#############################################', 'red')
            file_send_mod('./conf/chef/knife-zero/knife.rb', '/home/' + usernamek + '/my_chef_repo/', '600')

        try:
            with cd('/home/' + usernamek + '/my_chef_repo'):
                with open("./conf/servers/out_users_test.txt", "r") as pyfile:
                    serverlist = [lineIntext.split()[0] for lineIntext in pyfile]
                    for serverIp in serverlist:
                        client_index = 0
                        client_index += 1
                        run('knife zero bootstrap ' + usernamek + '@' + serverIp + ' -N client' + str(client_index))
                        # knife bootstrap node_domain_or_IP -x username -P password -N name_for_node --sudo

                sudo('knife node list')
                sudo('knife search node "name:cli*"')
                sudo('knife search node "platform:centos"')

                # knife ssh "platform:centos*" --ssh-user ebarrirero hostname
                # knife ssh "name:cli*" --ssh-user ebarrirero yum search vim

                # knife zero converge "name:client1" -x ebarrirero
                sudo('knife zero converge "name:*" --ssh-user' + usernamek)

                sudo('knife cookbook create create_file')

                for chef_envs in envs_list:
                    sudo('knife environment create ' + chef_envs + ' --disable-editing')
                """
                # knife node environment set client1 development
                # knife node environment set client2 production

                # knife search node "chef_environment:development
                # knife search node "chef_environment:development

                # knife role create frontend
                # knife role delete frontend
                """
        except SystemExit:
            print colored('########################################', 'red')
            print colored('###### knife zero config problem #######', 'red')
            print colored('########################################', 'red')


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

                    file_send_mod('/vagrant/scripts/conf/cachefs/cachefilesd.conf', '/etc/cachefilesd.conf', '664')
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


def nfs_server_ubuntu(nfs_dir):
    """
Install in the host7s NFS Server under Debian/Ubuntu based systems
    :param nfs_dir: NFS directory to be shared
    """
    with settings(warn_only=False):
        sudo('apt-get update')
        sudo('apt-get -y install nfs-kernel-server')

        if exists('/var/' + nfs_dir, use_sudo=True):
            print colored('###########################################', 'blue')
            print colored('####### Directory already created #########', 'blue')
            print colored('###########################################', 'blue')
        else:
            print colored('###########################################', 'red')
            print colored('###### Creating NFS share Directory #######', 'red')
            print colored('###########################################', 'red')
            sudo('mkdir /var/' + nfs_dir)
            # sudo('chmod -R 777 /var/'+nfs_dir+'/')
            sudo('chown nobody:nogroup /var/' + nfs_dir + '/')

        # sudo('chkconfig nfs on')
        # sudo('service rpcbind start')
        # sudo('service nfs start')

        # ip_addr = sudo('ifconfig eth0 | awk \'/inet /{print substr($2,6)}\'')
        # netmask = sudo('ifconfig eth0 | awk \'/inet /{print substr($4,6)}\'')
        # subnet_temp = iptools.ipv4.subnet2block(str(ip_addr) + '/' + str(netmask))
        # subnet = subnet_temp[0]
        # sudo('echo "/var/' + nfs_dir + '     ' + subnet + '/' + netmask +
        # '(rw,sync,no_root_squash,no_subtree_check)" > /etc/exports')
        sudo('echo "/var/' + nfs_dir + '     *(rw,sync,no_root_squash)" > /etc/exports')

        sudo('sudo exportfs -a')

        sudo('service nfs-kernel-server start')

        # sudo firewall-cmd --zone=public --add-service=nfs --permanent
        # sudo firewall-cmd --zone=public --add-service=rpc-bind --permanent
        # sudo firewall-cmd --zone=public --add-service=mountd --permanent
        # sudo firewall-cmd --reload


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


def mysql_install_client_centos7():
    """
Install the mysql client in a Centos7 based OS
    """
    with settings(warn_only=False):
        print colored('===========================', 'blue')
        print colored('INSTALLING : "MYSQL Client"', 'blue')
        print colored('===========================', 'blue')

        if exists('/etc/yum.repos.d/mysql-community.repo') and exists('/etc/yum.repos.d/mysql-community-source.repo'):
            print colored('############################################', 'blue')
            print colored('##### MySQL Repository already exists ######', 'blue')
            print colored('############################################', 'blue')
        else:
            sudo('wget -P /home/vagrant/ http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm')
            with cd('/home/vagrant/'):
                if exists('mysql-community-release-el7-5.noarch.rpm', use_sudo=True):
                    print colored('################################################', 'blue')
                    print colored('##### MySQL Repository File downloaded OK ######', 'blue')
                    print colored('################################################', 'blue')
                    try:
                        print colored('#########################################', 'blue')
                        print colored('####### ADDING MySQL Repository #########', 'blue')
                        print colored('#########################################', 'blue')
                        sudo('rpm -ivh mysql-community-release-el7-5.noarch.rpm')
                    except SystemExit:
                        print colored('##############################################', 'red')
                        print colored('####### FAIL to add MySQL repository #########', 'red')
                        print colored('##############################################', 'red')
                else:
                    print colored('######################################', 'red')
                    print colored('##### Repo File does not exists ######', 'red')
                    print colored('######################################', 'red')

        try:
            sudo('yum install -y mysql mysql-community-client')
        except SystemExit:
            print colored('#################################################', 'red')
            print colored('####### Problem installing MySQL CLIENT #########', 'red')
            print colored('#################################################', 'red')


def mysql_sh_db_user(mysql_user, mysql_ip="127.0.0.1"):
    """
MySQLdump backup
In case you have remote permissions with the mysql_user passed as argument
it's possible to run this fabric task with the "local" role.
fab -R local mysql_sh_db_user:root,192.168.0.1

If not yo can just pass de Servers fabric Role and the default mysql_ip
set as "127.0.0.1" (localhost) will be ok
fab -R devtest mysql_sh_db_user:root,127.0.0.1

    :param mysql_user: MySQL Server Admin user
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


def mysql_create_db(db_name, mysql_ip="127.0.0.1"):
    """
Create a MySQL Database with the given db_name
    :param db_name: Database name to be created
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "CREATE DATABASE ' + db_name + ';"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "show databases;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


def mysql_create_local_user(db_user, db_user_pass="password", mysql_ip="127.0.0.1"):
    """
Create a localhost MySQL user
    :param db_user: Username to be created
    :param db_user_pass: Password for the new username
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "CREATE USER ' + db_user + '@localhost IDENTIFIED BY'
                                                                                     ' \'' + db_user_pass + '\';"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


def mysql_grant_user_db(db_name, db_user, db_user_pass="db_user", mysql_ip="127.0.0.1"):
    """
Given the username, grant MySQL permissions for a certain DB to this username
    :param db_name: Database name to grant permissions in
    :param db_user: Database Username to grant access to the before passsed DB
    :param db_user_pass: Database Username password
    :param mysql_ip: MySQL Server IP Address

localhost] sudo: mysql -h 172.28.128.4 -u root -p -e "GRANT ALL PRIVILEGES ON wordpress.*
TO wordpressuer@localhost IDENTIFIED BY 'password';"
[localhost] out: Enter password:
[localhost] out: ERROR 1044 (42000) at line 1: Access denied for user 'root'@'172.28.128.3'
to database 'wordpress'
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "GRANT ALL PRIVILEGES ON ' + db_name + '.* TO '
                 + db_user + '@localhost IDENTIFIED BY \'' + db_user_pass + '\';"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


def mysql_grant_remote_cx(mysql_pass, remote_ip, mysql_ip="127.0.0.1"):
    """
Grant MySQL remote conection from a certain host
    :param mysql_pass: MySQL Server root password
    :param remote_ip: Remote host IP address to allow remote connections from
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "GRANT ALL PRIVILEGES ON *.* TO \'root\'@\''
                 + remote_ip + '\' IDENTIFIED BY \'' + mysql_pass + '\';"')
            # GRANT ALL PRIVILEGES ON *.* TO 'root'@'devops-chef-server-01' IDENTIFIED BY 'Temp01';
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "SELECT User, Host, Password FROM mysql.user;"')
            # DROP USER 'root'@'chef.grey.com';
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


def mysql_backup_all(local_dir, remote_dir, mysql_user, mysql_ip="127.0.0.1"):
    """
MySQLdump backup for all databases
fab -R devtest mysql_backup:/tmp/,/tmp/,root,127.0.0.1
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param remote_dir: mysqldump remote host destination directory
    :param mysql_user: MySQL Server Admin User
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
        # +--------------------+
        # | Database           |
        # +--------------------+
        # | information_schema |
        # | ggcc_prd           |
        # | innodb             |
        # | mysql              |
        # | performance_schema |
        # | tmp                |
        # +--------------------+

        # date = str(time.strftime("%x %X"))
        # date = date.replace("/", "-")
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        if os.path.isdir(local_dir) and exists(remote_dir):
            sudo('mysqldump -Q -q -e -R --add-drop-table -A --single-transaction -u '
                 + mysql_user + ' -p --all-databases > ' + remote_dir + 'backup-' + date + '.sql')
            # check that the backup was created with a grep.
            get(remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + "-" + env.host + '.sql',
                use_sudo=True)
            sudo('rm -rf ' + remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + '.sql')
        else:
            print colored('===================================================', 'red')
            print colored('Check that DIRs: ' + local_dir + ' & ' + remote_dir + ' do exist', 'red')
            print colored('===================================================', 'red')


def mysql_restore_upgrade_all(mysqldump_fname, local_dir, remote_dir, mysql_user, mysql_ip="127.0.0.1"):
    """
MySQLdump restore and upgrade for all DBs
eg: fab -R devtest mysql_restore_upgrade:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,/tmp/,root,127.0.0.1
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param remote_dir: mysqldump remote host destination directory
    :param mysql_user: MySQL Server Admin User
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        if os.path.isfile(local_dir + mysqldump_fname):
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
            if exists(remote_dir):
                file_send_oldmod(local_dir + mysqldump_fname, remote_dir + mysqldump_fname)
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p < ' + remote_dir + mysqldump_fname)
                sudo('mysql_upgrade -h ' + mysql_ip + ' -u ' + mysql_user + ' -p')
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
        else:
            print colored('===================================================', 'red')
            print colored('Check that DIRs: ' + local_dir + mysqldump_fname + ' do exist', 'red')
            print colored('===================================================', 'red')


def mysql_backup_db(local_dir, remote_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
    """
MySQLdump backup for a certain DB passed as argument
fab -R devtest mysql_backup:/tmp/,/tmp/,root,127.0.0.1
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param remote_dir: mysqldump remote host destination directory
    :param mysql_user: MySQL Server Admin User
    :param db_name: MySQL Server DB name to be backuped
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;" | grep ' + db_name)
        # +--------------------+
        # | Database           |
        # +--------------------+
        # | information_schema |
        # | ggcc_prd           |
        # | innodb             |
        # | mysql              |
        # | performance_schema |
        # | tmp                |
        # +--------------------+

        # date = str(time.strftime("%x %X"))
        # date = date.replace("/", "-")
        # date = date.replace("/", "-")
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        if database != "":
            if os.path.isdir(local_dir) and exists(remote_dir):
                sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                     ' -u ' + mysql_user + ' -p ' + db_name + ' > ' + remote_dir + 'backup-' + date + '.sql')
                # check that the backup was created with a grep.
                get(remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + "-" + env.host + '.sql',
                    use_sudo=True)
                sudo('rm -rf ' + remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + '.sql')
            else:
                print colored('===================================================', 'red')
                print colored('Check that DIRs: ' + local_dir + ' & ' + remote_dir + ' do exist', 'red')
                print colored('===================================================', 'red')
        else:
            print colored('=========================================', 'red')
            print colored('Database : ' + db_name + ' does not exist', 'red')
            print colored('=========================================', 'red')


def mysql_backup_db_from_conf(local_dir, remote_dir, db_name, mysql_ip="127.0.0.1"):
    """
MySQLdump backup for a certain DB passed as argument
fab -R devtest mysql_backup:/tmp/,/tmp/,root,127.0.0.1
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param remote_dir: mysqldump remote host destination directory
    :param db_name: MySQL Server DB name to be backuped
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        mysql_user = load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "username")
        mysql_password_enc = str(load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "password"))
        password = password_base64_decode(mysql_password_enc)

        with hide('running', 'stdout'):
            database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                            ' -e "show databases;" | grep ' + db_name)

            date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

            if database != "":
                if os.path.isdir(local_dir) and exists(remote_dir):
                    sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                         ' -u ' + mysql_user + ' -p' + password + ' ' + db_name + ' > ' +
                         remote_dir + 'backup-' + date + '.sql')
                    # check that the backup was created with a grep.

                    print colored('============================================================================',
                                  'blue')
                    print colored('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                                  ' -u ' + mysql_user + ' -p ' + db_name + ' > ' +
                                  remote_dir + 'backup-' + date + '.sql', 'blue')
                    print colored('============================================================================',
                                  'blue')

                    get(remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + "-" + env.host + '.sql',
                        use_sudo=True)
                    print colored('============================================================================',
                                  'blue')
                    print colored('get(' + remote_dir + 'backup-' + date + '.sql,' + local_dir + 'backup-' + date + "-"
                                  + env.host + '.sql', 'blue')
                    print colored('============================================================================',
                                  'blue')

                    sudo('rm -rf ' + remote_dir + 'backup-' + date + '.sql', local_dir + 'backup-' + date + '.sql')
                    print colored('============================================================================',
                                  'blue')
                    print colored('rm -rf ' + remote_dir + 'backup-' + date + '.sql,' + local_dir + 'backup-' + date +
                                  '.sql', 'blue')
                    print colored('============================================================================',
                                  'blue')

                else:
                    print colored('===================================================', 'red')
                    print colored('Check that DIRs: ' + local_dir + ' & ' + remote_dir + ' do exist', 'red')
                    print colored('===================================================', 'red')
            else:
                print colored('=========================================', 'red')
                print colored('Database : ' + db_name + ' does not exist', 'red')
                print colored('=========================================', 'red')


def mysql_backup_db_rds(local_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
    """
MySQLdump backup for a certain DB passed as argument
fab -R local mysql_backup:/tmp/,root,testdb,ggcc-prd.xxyyzzuuiioo.us-east-1.rds.amazonaws.com
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param mysql_user: MySQL Server Admin User
    :param db_name: MySQL Server DB name to be backuped
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;" | grep ' + db_name)
        # +--------------------+
        # | Database           |
        # +--------------------+
        # | information_schema |
        # | ggcc_prd           |
        # | innodb             |
        # | mysql              |
        # | performance_schema |
        # | tmp                |
        # +--------------------+

        # date = str(time.strftime("%x %X"))
        # date = date.replace("/", "-")
        # date = date.replace("/", "-")
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        if database != "":
            if os.path.isdir(local_dir):
                sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                     ' -u ' + mysql_user + ' -p ' + db_name + ' > ' + local_dir + db_name + '-bak-'
                     + date + '.sql')
                # check that the backup was created with a grep.
            else:
                print colored('============================================', 'red')
                print colored('Check that DIR: ' + local_dir + ' does exist', 'red')
                print colored('============================================', 'red')
        else:
            print colored('=========================================', 'red')
            print colored('Database : ' + db_name + ' does not exist', 'red')
            print colored('=========================================', 'red')


def mysql_backup_db_rds_from_conf(local_dir, db_name):
    """
MySQLdump backup for a certain DB passed as argument
fab -R localhost mysql_backup:/tmp/,testdb
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Server DB name to be backuped

    """
    with settings(warn_only=False):
        mysql_ip = load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "host")
        mysql_user = load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "username")
        mysql_password_enc = str(load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "password"))
        password = password_base64_decode(mysql_password_enc)
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isdir(local_dir):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name)

                    parts = database.split('\n')
                    database = parts[1]

                    if database == db_name:
                        sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                             ' -u ' + mysql_user + ' -p' + password + ' ' + db_name + ' > ' + local_dir + db_name + '-bak-'
                             + date + '.sql')
                        # check that the backup was created with a grep.

                        print colored('============================================================================',
                                      'blue')
                        print colored('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                                      ' -u ' + mysql_user + ' -p ' + db_name + ' > ' + local_dir + db_name + '-bak-'
                                      + date + '.sql', 'blue')
                        print colored('============================================================================',
                                      'blue')
                    else:
                        print colored('=========================================', 'red')
                        print colored('Database : ' + db_name + ' does not exist', 'red')
                        print colored('=========================================', 'red')

                else:
                    print colored('=============================================', 'red')
                    print colored('Check that DIRs: ' + local_dir + ' does exist', 'red')
                    print colored('=============================================', 'red')

            except SystemExit:
                print colored('=========================================', 'red')
                print colored('Database : ' + db_name + ' does not exist', 'red')
                print colored('=========================================', 'red')


def mysql_restore_to_new_db(mysqldump_fname, local_dir, remote_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
    """
MySQLdump restore
eg: fab -R devtest mysql_restore_to_new_db:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,/tmp/,root,127.0.0.1
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param remote_dir: mysqldump remote host destination directory
    :param mysql_user: MySQL Server Admin User
    :param db_name: MySQL Database name to be restored
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;" | grep ' + db_name)
        if os.path.isfile(local_dir + mysqldump_fname) and database != "":
            if exists(remote_dir):
                file_send_oldmod(local_dir + mysqldump_fname, remote_dir + mysqldump_fname)
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "CREATE DATABASE ' + db_name + date + ';"')
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p ' + db_name + date + ' < ' + remote_dir +
                     mysqldump_fname)
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
        else:
            print colored('===================================================', 'red')
            print colored('Check that DIRs: ' + local_dir + mysqldump_fname + ' do exist', 'red')
            print colored('===================================================', 'red')
            print colored('===================================================', 'red')
            print colored('Database: ' + database + ' already exists', 'red')
            print colored('===================================================', 'red')


def mysql_restore_rds_to_new_db(mysqldump_fname, local_dir, db_name):
    """
MySQLdump restore
eg: fab -R localhost mysql_restore_rds_to_new_db:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,testdb
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Database name to be restored

    """
    with settings(warn_only=False):
        mysql_ip = load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "host")
        mysql_user = load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "username")
        mysql_password_enc = str(load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql", "password"))
        password = password_base64_decode(mysql_password_enc)
        date = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isfile(local_dir + mysqldump_fname):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name)

                    parts = database.split('\n')
                    database = parts[1]

                    # if database != "" and db_name in database:
                    if database == db_name:
                        sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password + ' -e "CREATE DATABASE '
                            + db_name + '_' + date + ';"')
                        sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password + ' '
                            + db_name + '_' + date + ' < ' + local_dir + mysqldump_fname)
                        sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password + ' -e "show databases;"')
                    else:
                        print colored('==========================================', 'red')
                        print colored('Database: ' + database + ' does not exists', 'red')
                        print colored('==========================================', 'red')
                else:
                    print colored('===============================================================', 'red')
                    print colored('Check that file: ' + local_dir + mysqldump_fname + ' does exist', 'red')
                    print colored('===============================================================', 'red')
            except SystemExit:
                print colored('=========================================', 'red')
                print colored('Database: ' + db_name + ' does not exists', 'red')
                print colored('=========================================', 'red')


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


def install_lamp_centos7():
    """
LAMP Stack installation in Centos7 OS.
    """
    with settings(warn_only=False):
        sudo('yum update')
        sudo('yum install epel-release')
        print colored('=================================', 'blue')
        print colored('INSTALLING : "APACHE2 WebqServer"', 'blue')
        print colored('=================================', 'blue')
        # https://secure.kreationnext.com/support/the-perfect-server-centos-7-2-with-apache-
        # postfix-dovecot-pure-ftpd-bind-and-ispconfig-3-1/
        # MOD PYTHON COMPILE!!!
        #
        try:
            sudo('yum install -y httpd-manual-2.2.3-91.el5.centos httpd-2.2.3-91.el5.centos')
            sudo('systemctl start httpd.service')
            sudo('systemctl enable httpd.service')
        except SystemExit:
            sudo('yum install -y httpd')
            sudo('systemctl start httpd.service')
            sudo('systemctl enable httpd.service')
            sudo('chkconfig httpd on')

        print colored('===========================', 'blue')
        print colored('INSTALLING : "MYSQL Server"', 'blue')
        print colored('===========================', 'blue')

        if exists('/etc/yum.repos.d/mysql-community.repo') and exists('/etc/yum.repos.d/mysql-community-source.repo'):
            print colored('############################################', 'blue')
            print colored('##### MySQL Repository already exists ######', 'blue')
            print colored('############################################', 'blue')
        else:
            sudo('wget -P /home/vagrant/ http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm')
            with cd('/home/vagrant/'):
                if exists('mysql-community-release-el7-5.noarch.rpm', use_sudo=True):
                    print colored('################################################', 'blue')
                    print colored('##### MySQL Repository File downloaded OK ######', 'blue')
                    print colored('################################################', 'blue')
                    try:
                        print colored('#########################################', 'blue')
                        print colored('####### ADDING MySQL Repository #########', 'blue')
                        print colored('#########################################', 'blue')
                        sudo('rpm -ivh mysql-community-release-el7-5.noarch.rpm')
                    except SystemExit:
                        print colored('##############################################', 'red')
                        print colored('####### FAIL to add MySQL repository #########', 'red')
                        print colored('##############################################', 'red')
                else:
                    print colored('######################################', 'red')
                    print colored('##### Repo File does not exists ######', 'red')
                    print colored('######################################', 'red')

        try:
            sudo('yum install -y mysql-server-5.0.95-5.el5_9 mod_auth_mysql-3.0.0-3.2.el5_3 '
                 'MySQL-python-1.2.3-0.1.c1.el5')
            sudo('yum install -y mysql-devel-5.0.95-5.el5_9 perl-DBD-MySQL-3.0007-2.el5'
                 ' mysql-connector-odbc-3.51.26r1127-2.el5')
            sudo('yum install -y libdbi-dbd-mysql-0.8.1a-1.2.2 mysql-5.0.95-5.el5_9')
            sudo('systemctl start mysqld')
            sudo('mysql_secure_installation')
            sudo('chkconfig mysqld on')
        except SystemExit:
            sudo('yum install -y mysql-server mod_auth_mysql MySQL-python')
            sudo('yum install -y mysql-devel perl-DBD-MySQL mysql mysql-connector-odbc')
            sudo('yum install -y libdbi-dbd-mysql')
            sudo('systemctl start mysqld')
            sudo('mysql_secure_installation')
            sudo('chkconfig mysqld on')

        print colored('==================', 'blue')
        print colored('INSTALLING : "PHP"', 'blue')
        print colored('==================', 'blue')
        # opcache (a partir de 5.6)
        try:
            sudo('yum install -y php53-xml-5.3.3-26.el5_11 php53-dba-5.3.3-26.el5_11 php53-pspell-5.3.3-26.el5_11'
                 ' php53-5.3.3-26.el5_11')
            sudo('yum install -y php53-devel-5.3.3-26.el5_11 php53-common-5.3.3-26.el5_11 php53-bcmath-5.3.3-26.el5_11'
                 ' php53-intl-5.3.3-26.el5_11')
            sudo('yum install -y php53-mapi-7.1.14-1.el5 php53-interbase-5.3.3-1.el5 php53-recode-5.3.3-1.el5'
                 ' php53-mcrypt-5.3.3-1.el5')
            sudo('yum install -y php53-pdo-5.3.3-26.el5_11 php53-odbc-5.3.3-26.el5_11 php53-process-5.3.3-26.el5_11'
                 ' php53-imap-5.3.3-26.el5_11')
            sudo('yum install -y php53-gd-5.3.3-26.el5_11 php53-cli-5.3.3-26.el5_11 php53-xmlrpc-5.3.3-26.el5_11'
                 ' php53-ldap-5.3.3-26.el5_11')
            sudo('yum install -y php53-enchant-5.3.3-1.el5 php53-php-gettext-1.0.11-3.el5 php53-snmp-5.3.3-26.el5_11'
                 ' php53-tidy-5.3.3-1.el5')
            sudo('yum install -y php53-pgsql-5.3.3-26.el5_11 php53-soap-5.3.3-26.el5_11 php53-mssql-5.3.3-1.el5')
            sudo('yum install -y php53-mysql-5.3.3-26.el5_11 php53-mbstring-5.3.3-26.el5_11')
            sudo('systemctl restart httpd.service')
            sudo('firewall-cmd --permanent --zone=public --add-service=http')
            sudo('firewall-cmd --permanent --zone=public --add-service=https')
            sudo('firewall-cmd --reload')
        except SystemExit:
            sudo('yum install -y php php-mysql php-devel php-common php-gd php-cli')
            sudo('yum install -y php53-xml php53-dba php53-pspell php-bcmath php-intl php53-mapi '
                 'php-interbase php-recode php-mcrypt php-pdo php-odbc php-process php-imap php-xmlrpc php-ldap')
            sudo('yum install -y php-enchant php-php-gettext php-snmp php-tidy')
            sudo('yum install -y php-pgsql php-soap php-mssql php-mbstring')
            sudo('systemctl restart httpd.service')
            try:
                sudo('firewall-cmd --permanent --zone=public --add-service=http')
                sudo('firewall-cmd --permanent --zone=public --add-service=https')
                sudo('firewall-cmd --reload')
            except SystemExit:
                print colored('#################################', 'red')
                print colored('##### Firewall not running ######', 'red')
                print colored('#################################', 'red')

                # [ebarrirero@nyc1app204 shibboleth]$ sudo rpm -ql php53
                # /etc/httpd/conf.d/php.conf
                # /usr/lib64/httpd/modules/libphp5.so
                # /var/lib/php/session
                # /var/www/icons/php.gif


def install_various_centos7():
    """
Install custom list of packets
    """
    with settings(warn_only=False):
        print colored('============================', 'blue')
        print colored('INSTALLING : SHIBBOLETH Auth', 'blue')
        print colored('============================', 'blue')
        try:
            sudo('curl -o /etc/yum.repos.d/shibboleth.repo '
                 'http://download.opensuse.org/repositories/security://shibboleth/CentOS_7/security:shibboleth.repo')
            sudo('yum install -y shibboleth-2.5.6-3.1')
            sudo('systemctl start shibd.service')
            sudo('chkconfig --levels 345 shibd on')

        except SystemExit:
            sudo('curl -o /etc/yum.repos.d/shibboleth.repo '
                 'http://download.opensuse.org/repositories/security://shibboleth/CentOS_7/security:shibboleth.repo')
            sudo('yum install -y shibboleth')
            sudo('systemctl start shibd.service')
            sudo('chkconfig --levels 345 shibd on')

        print colored('===================', 'blue')
        print colored('INSTALLING : "CRON"', 'blue')
        print colored('===================', 'blue')
        sudo('yum install -y crontabs anacron vixie-cron')

        print colored('===================================', 'blue')
        print colored('INSTALLING : "NEW RELIC" Monitoring', 'blue')
        print colored('===================================', 'blue')

        if exists('/etc/yum.repos.d/newrelic.repo'):
            print colored('###############################################', 'blue')
            print colored('##### NewRelic Repository already exists ######', 'blue')
            print colored('###############################################', 'blue')
        else:
            try:
                print colored('############################################', 'blue')
                print colored('####### ADDING NreRelic Repository #########', 'blue')
                print colored('############################################', 'blue')
                sudo('rpm -Uvh https://yum.newrelic.com/pub/newrelic/el5/x86_64/newrelic-repo-5-3.noarch.rpm')
            except SystemExit:
                print colored('##############################################', 'red')
                print colored('##### FAIL to add NewRelic repository ########', 'red')
                print colored('##############################################', 'red')

        sudo('yum install -y newrelic-php5 newrelic-repo newrelic-daemon newrelic-php5-common newrelic-sysmond')

        try:
            # nrsysmond-config --set license_key=YOUR_9LICENSE_KEY
            sudo('/etc/init.d/newrelic-sysmond start')
        except SystemExit:
            print colored('###########################################', 'red')
            print colored('##### FAIL to start NewRelic agent ########', 'red')
            print colored('###########################################', 'red')

        print colored('======================', 'blue')
        print colored('INSTALLING : "POSTFIX"', 'blue')
        print colored('======================', 'blue')
        sudo('yum install -y postfix')

        print colored('==================', 'blue')
        print colored('INSTALLING : "NTP"', 'blue')
        print colored('==================', 'blue')
        sudo('yum install -y ntp')

        print colored('============================', 'blue')
        print colored('INSTALLING : "SNMP"', 'blue')
        print colored('============================', 'blue')
        sudo('yum install -y net-snmp-libs net-snmp net-snmp-utils')


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


def rsync_data_from_server(data_dir="/tmp/"):
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


def rsync_data_to_server(data_dir="/tmp/"):
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
        rsync_data_to_server_v2(data_dir, data_dir + 'var-www.2016-09-30-15-00-16.tar.gz',
                                data_dir + 'var/www/', remote_dir + 'var/www/')

        print colored('=========================', 'blue')
        print colored('SYNC: Apache Config Files', 'blue')
        print colored('=========================', 'blue')
        rsync_data_to_server_v2(data_dir, data_dir + 'etc-httpd.2016-09-30-15-36-19.tar.gz',
                                data_dir + 'etc/httpd/', remote_dir + 'etc/httpd/')

        print colored('======================', 'blue')
        print colored('SYNC: PHP Config Files', 'blue')
        print colored('======================', 'blue')
        # file_send_oldmod(data_dir + 'php.ini', remote_dir + '/etc/')
        rsync_data_to_server_v2(data_dir, data_dir + 'etc-php.d.2016-09-30-15-36-47.tar.gz',
                                data_dir + 'etc/php.d/', remote_dir + 'etc/php.d/')
        rsync_data_to_server_v2(data_dir, data_dir + 'usr-include-php.2016-09-30-15-36-48.tar.gz',
                                data_dir + 'usr/include/php/', remote_dir + 'usr/include/php/')

        print colored('=============================', 'blue')
        print colored('SYNC: Shibboleth Config Files', 'blue')
        print colored('=============================', 'blue')
        rsync_data_to_server_v2(data_dir, data_dir + 'etc-shibboleth.2016-09-30-15-36-51.tar.gz',
                                data_dir + 'etc/shibboleth/', remote_dir + 'etc/shibboleth/')
        key_remove("root")


def rsync_data_to_server_v2(local_file_dir, local_file_path, local_rsync_dir, remote_dir):
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


def php53_install_centos7():
    """
Install php-5.3.29 in a CentOS7 Server
    """
    with settings(warn_only=False):
        sudo('yum groupinstall \'Development Tools\'')
        sudo('yum install -y libxml2-devel libXpm-devel gmp-devel libicu-devel t1lib-devel aspell-devel'
             ' openssl-devel openssl openssl-common bzip2-devel libcurl-devel libjpeg-devel libvpx-devel libpng-devel'
             ' freetype-devel readline-devel libtidy-devel libxslt-devel libmcrypt-devel pcre-devel curl-devel'
             ' mysql-devel ncurses-devel gettext-devel net-snmp-devel libevent-devel libtool-ltdl-devel'
             ' libc-client-devel postgresql-devel enchant-devel libpng-devel pam-devel libdb libdb-devel'
             ' freetds-devel recode-devel mod_ldap httpd-devel')
        with cd('/usr/src'):
            if exists('/usr/src/php-5.3.29', use_sudo=True):
                print colored('###########################################', 'blue')
                print colored('##### PHP Sources already downloaded ######', 'blue')
                print colored('###########################################', 'blue')
                with cd('php-5.3.29'):
                    sudo('./configure  --enable-cli --with-pgsql --with-curl --with-openssl --enable-pdo --with-gettext'
                         ' --enable-mbstring --with-apxs2 --with-gd --with-zlib --with-ldap --with-pspell --with-mcrypt'
                         ' --with-imap-ssl --with-tidy --with-enchant --enable-soap --with-mssql --with-mysql'
                         ' --with-mysqli'
                         ' --enable-mbstring --enable-xml --enable-libxml --with-xmlrpc'
                         ' --with-config-file-scan-dir=/etc/php.d/ --with-jpeg-dir=/lib64/ --with-libdir=lib64')
                    sudo('make')
                    sudo('make install')
            else:
                print colored('###########################################################', 'red')
                print colored('###### PHP Sources will be downloaded and installed #######', 'red')
                print colored('###########################################################', 'red')
                sudo('wget "http://php.net/get/php-5.3.29.tar.gz/from/this/mirror"')
                sudo('mv mirror php.tar.gz')
                sudo('tar -xzf php.tar.gz')
                with cd('/usr/src/php-5.3.29'):
                    sudo('./configure  --enable-cli --with-pgsql --with-curl --with-openssl --enable-pdo --with-gettext'
                         ' --enable-mbstring --with-apxs2 --with-gd --with-zlib --with-ldap --with-pspell --with-mcrypt'
                         ' --with-imap-ssl --with-tidy --with-enchant --enable-soap --with-mssql --with-mysql'
                         ' --with-mysqli'
                         ' --enable-mbstring --enable-xml --enable-libxml --with-xmlrpc'
                         ' --with-config-file-scan-dir=/etc/php.d/ --with-jpeg-dir=/lib64/ --with-libdir=lib64')
                    sudo('make')
                    sudo('make install')


def php53_remove_centos7():
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


def password_hash(password):
    """
Password hash func
    :param password: plaintext password to be hashed
    """
    with settings(warn_only=False):
        hash_pass = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        # plainpass = pbkdf2_sha256.decrypt(hash, rounds=200000, salt_size=16)
        return hash_pass


def password_hash_verify(password, hash_password):
    """
Password hash verify func
    :param password: plaintext password to be hashed
    :param hash_password: password hash of the pass to be verified
    """
    with settings(warn_only=False):
        if pbkdf2_sha256.verify(password, hash_password):
            print "Correct Pass"
        else:
            print "Incorrect Pass"


def password_base64_encode(password):
    """
Password base64 encode
    :param password: plaintext password to be hashed

    eg: [vagrant@server proton]$ fab -R local password_base64_encode:Testing!
    [localhost] Executing task 'password_base64_encode'
    VGVzdGluZyE=
    Done.

    """
    with settings(warn_only=False):
        password_base64 = base64.b64encode(password)
        print password_base64
        return str(password_base64)


def password_base64_decode(password_base64):
    """
Password base64 decode
    :param password_base64: base64 encoded password

    eg: [vagrant@server proton]$ fab -R local password_base64_decode:"VGVzdGluZyE\="
    [localhost] Executing task 'password_base64_decode'
    Testing!
    Done.
    """
    with settings(warn_only=False):
        password = base64.b64decode(password_base64)
        # print password
        return str(password)


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
def db_backup():
    with settings(warn_only=False):
        #Check the DBs in PRD
        mysql -h ggcc-prd.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "show databases"
        +--------------------+
        | Database           |
        +--------------------+
        | information_schema |
        | ggcc_prd           |
        | innodb             |
        | mysql              |
        | performance_schema |
        | tmp                |
        +--------------------+

        mysql -h ggcc-prd.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "use ggcc_prd; show tables;"

        Database changed
        mysql> show tables;
        +----------------------------+
        | Tables_in_ggcc_prd         |
        +----------------------------+
        | category                   |
        | category_votes             |
        | category_weights           |
        | contest                    |
        | contest_agencies           |
        | contest_grouping           |
        | contest_status             |
        | contest_submitters_judges  |
        | contest_view               |
        | delayed_action             |
        | groups                     |
        | migrations                 |
        | report_shared              |
        | sessions                   |
        | stage                      |
        | submission                 |
        | submission_awards          |
        | submission_categories      |
        | submission_comments        |
        | submission_downloads       |
        | submission_favorite_shared |
        | submission_favorited       |
        | submission_files           |
        | submission_tags            |
        | submission_votes           |
        | throttle                   |
        | users                      |
        | users_groups               |
        | view                       |
        +----------------------------+
        29 rows in set (0.00 sec)

        mysql> SELECT table_name "Table Name", table_rows "Rows Count", round(((data_length + index_length)/1024/1024),2) "Table Size (MB)" FROM information_schema.TABLES WHERE table_schema = "ggcc_prd";

        mysql> select * from  mysql.user;
        mysql> describe mysql.user;

        mysql> select User from mysql.user;
        +----------------+
        | User           |
        +----------------+
        | grey_ggcc_user |
        | greyrdsadmin   |
        | rdsadmin       |
        +----------------+
        3 rows in set (0.00 sec)

        mysql> show grants for 'greyrdsadmin'@'%';
        mysql> show grants for 'grey_ggcc_user'@'%';

        mysql> show grants for 'greyrdsadmin'@'%';
        +-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Grants for greyrdsadmin@%                                                                                                                                                                                                                                                                                                                                                                                 |
        +-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, RELOAD, PROCESS, REFERENCES, INDEX, ALTER, SHOW DATABASES, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE, REPLICATION SLAVE, REPLICATION CLIENT, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, CREATE USER, EVENT, TRIGGER ON *.* TO 'greyrdsadmin'@'%' IDENTIFIED BY PASSWORD '*A585F04D9672D0A452EACF9A19845977F7B69AD3' WITH GRANT OPTION |
        +-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        1 row in set (0.01 sec)

        mysql> show grants for 'grey_ggcc_user'@'%';
        +---------------------------------------------------------------------------------------------------------------+
        | Grants for grey_ggcc_user@%                                                                                   |
        +---------------------------------------------------------------------------------------------------------------+
        | GRANT USAGE ON *.* TO 'grey_ggcc_user'@'%' IDENTIFIED BY PASSWORD '*0A52185901D9594418AFD3E33EF316C384DDCAF2' |
        | GRANT ALL PRIVILEGES ON `ggcc_prd`.* TO 'grey_ggcc_user'@'%' WITH GRANT OPTION                                |
        +---------------------------------------------------------------------------------------------------------------+
        2 rows in set (0.00 sec)

        [ebarrirero@jumphost ~]$ df -h
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/xvdi        99G   89G  4,7G  96% /ops/backups
        [ebarrirero@jumphost ~]$ cd /ops/backups/

        [ebarrirero@jumphost backups]$ ls -ltr
        total 49104192
        -rw-r--r--  1 jenkins jenkins 16255091287 ago 25 16:54 greycom-prd-2016-08-25.tar.gz
        -rw-r--r--  1 jenkins jenkins 16263377824 ago 30 18:07 greycom-prd-2016-08-30.tar.gz
        -rw-r--r--  1 jenkins jenkins 16275778219 sep  1 19:23 greycom-prd-2016-09-01.tar.gz

        [ebarrirero@jumphost backups]$ sudo rm -rf greycom-prd-2016-08-25.tar.gz
        [ebarrirero@jumphost backups]$ sudo rm -rf greycom-prd-2016-08-30.tar.gz

        [ebarrirero@jumphost backups]$ df -h
        /dev/xvdi        99G   59G   35G  63% /ops/backups


        DATE=`date +%Y-%m-%d`
        mysqldump -q -c --routines --triggers --single-transaction -h ggcc-prd.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p ggcc_prd > /ops/backups/ggcc_prd-$DATE.sql
        mysqldump -q -c --routines --triggers --single-transaction -h ggcc-prd.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p ggcc_prd > /ops/backups/ggcc_prd-$DATE.sql

        #check that the backup was created with a grep.

        #mysql --defaults-file=scripts/conf/connect-stg/connect-stg-my.cnf -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -e "CREATE DATABASE grey_stg_v2"
        #mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "DROP DATABASE grey_stg_v2"
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "CREATE DATABASE ggcc_stg_v3"
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "CREATE DATABASE ggcc_stg_v4"
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "show databases;"
        Enter password:
        +--------------------+
        | Database           |
        +--------------------+
        | information_schema |
        | ggcc_stg           |
        | ggcc_stg_v1        |
        | ggcc_stg_v2        |
        | innodb             |
        | mysql              |
        | performance_schema |
        | tmp                |
        +--------------------+

        DATE=`date +%Y-%m-%d`
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p ggcc_stg_v3 < /ops/backups/ggcc_prd-$DATE.sql
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p ggcc_stg_v4 < /ops/backups/ggcc-prd-$DATE.sql

        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "use ggcc_stg_v4; show tables;"

        THEN IN STG
        If User not created:
        mysql> CREATE USER 'grey_ggcc_user'@'%' IDENTIFIED BY 'grey_ggcc_user';
        Query OK, 0 rows affected (0.01 sec)

        #To grant permisions for a certain user for one DB (* represents the tables)
        #mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "grant all privileges on ggcc_stg_v2.* to 'grey_ggcc_user'@'%' WITH GRANT OPTION;"
        #mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "grant all privileges on ggcc_stg_v2.* to 'grey_ggcc_user'@'%';"

        #To grant permisions for a certain user for a specific DB (for Connect)
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "grant all on ggcc_stg_v3.* to 'ggcc_stg_user'@'%';"
        mysql -h ggcc-stg.cqrpklcv3mzd.us-east-1.rds.amazonaws.com -u greyrdsadmin -p -e "grant all on ggcc_stg_v4.* to 'ggcc_stg_user'@'%';"

        #Remove the dump

        #Extra - adding a certain host to root user
        mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'chef.grey.com' IDENTIFIED BY 'Temp01';
        Query OK, 0 rows affected (0.12 sec)

        mysql> SELECT User, Host, Password FROM mysql.user;
        +----------------+----------------------------+------------------+
        | User           | Host                       | Password         |
        +----------------+----------------------------+------------------+
        | root           | localhost                  | 365fe285580134fc |
        | root           | nyc1app202.ggg.grey.global |                  |
        | root           | 127.0.0.1                  |                  |
        |                | localhost                  |                  |
        |                | nyc1app202.ggg.grey.global |                  |
        | buddy          | localhost                  | 687bda6114dbbe68 |
        | q2a            | localhost                  | 51c6a9a9362c2c8f |
        | bu_user        | localhost                  | 38a1f09a2141ea8a |
        | buddy          | %                          | 687bda6114dbbe68 |
        | newuser        | %                          | 365fe285580134fc |
        | yourlsdev_user | localhost                  | 619850b40fb16757 |
        | root           | chef.grey.com              | 365fe285580134fc |
        +----------------+----------------------------+------------------+
        12 rows in set (0.00 sec)

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
