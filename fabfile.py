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

from fabric.api import env

import config

"""
# from fabric.api import hosts, sudo, settings, hide, env, execute, prompt, run, local, task, put, cd, get
# from fabric.colors import red, blue, yellow, green
# from fabric.contrib.files import append, exists, sed
# from fabric.contrib.files import exists, sed, task
# from fabric.contrib.files import exists, task
# from termcolor import colored
# from fabric.contrib.project import rsync_project, upload_project
# from distutils.util import strtobool

# import iptools
# import time
# import ConfigParser
# from optparse import OptionParser
# from time import gmtime, strftime
# from passlib.hash import pbkdf2_sha256
"""

from modules import chef_fab, conf_files_fab, download_files_fab, file_fab, inst_centos_7_fab, haproxy_fab, \
    inst_ubu_14_fab, key_fab, maltrail_fab, mysql_fab, nfs_fab, os_fab, passwd_fab, pkg_mgr_fab, rm_centos_7_fab, \
    rsync_fab, show_fab, upload_files_fab, users_fab, aws_fab

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