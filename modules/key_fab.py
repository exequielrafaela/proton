# Import Fabric's API module#
import getpass
import os

import pwd
from fabric.api import settings, env, sudo, local
from fabric.contrib.files import exists, append
from fabric.decorators import task
# from fabric.tasks import Task
from termcolor import colored


# class GenUser(Task):
#     name = 'gen'
#
#     def gen_user(self, usernameg=""):
#         """
#      Generate an SSH key for a certain user
#      Remember that this task it's intended to be run with role "local"
#         cmd: fab gen
#         :type usernameg:
#         :param usernameg: "username" to change password
#         """
#         pass
#         with settings(warn_only=False):
#             # usernameg = prompt("Which USERNAME you like to GEN KEYS?")
#             # user_exists = sudo('cut -d: -f1 /etc/passwd | grep '+usernameg)
#             # user_exists = sudo('cat /etc/passwd | grep ' + usernameg)
#             # user_exists = ""
#             try:
#                 user_struct = pwd.getpwnam(usernameg)
#                 user_exists = user_struct.pw_gecos.split(",")[0]
#                 print colored(user_exists, 'green')
#                 if user_exists == "root":
#                     print colored('#################################################################', 'yellow')
#                     print colored('CAREFULL: ROOT ssh keys will be generated if they does not exists', 'yellow')
#                     print colored('#################################################################', 'yellow')
#                     if os.path.exists('/' + usernameg + '/.ssh/id_rsa'):
#                         print colored(str(os.path.exists('/' + usernameg + '/.ssh/id_rsa')), 'blue')
#                         print colored('###########################################', 'blue')
#                         print colored('username: ' + usernameg + ' KEYS already EXISTS', 'blue')
#                         print colored('###########################################', 'blue')
#                     else:
#                         print colored('###########################################', 'blue')
#                         print colored('username: ' + usernameg + ' Creating KEYS', 'blue')
#                         print colored('###########################################', 'blue')
#                         sudo("ssh-keygen -t rsa -f /" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
#                         # http://unix.stackexchange.com/questions/36540/why-am-i-still-getting-a-
#                         password-prompt-with-ssh
#                         # -with-public-key-authentication
#                         # sudo('chmod 700 /home/' + usernameg)
#                         sudo('chmod 755 /' + usernameg)
#                         sudo('chmod 755 /' + usernameg + '/.ssh')
#                         sudo('chmod 600 /' + usernameg + '/.ssh/id_rsa')
#
#                 elif os.path.exists('/home/' + usernameg + '/.ssh/id_rsa'):
#                     print colored(str(os.path.exists('/home/' + usernameg + '/.ssh/id_rsa')), 'blue')
#                     print colored('###########################################', 'blue')
#                     print colored('username: ' + usernameg + ' KEYS already EXISTS', 'blue')
#                     print colored('###########################################', 'blue')
#                 else:
#                     print colored('###########################################', 'blue')
#                     print colored('username: ' + usernameg + ' Creating KEYS', 'blue')
#                     print colored('###########################################', 'blue')
#                     sudo("ssh-keygen -t rsa -f /home/" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
#                     # http://unix.stackexchange.com/
#                       questions/36540/why-am-i-still-getting-a-password-prompt-with-ssh
#                     # -with-public-key-authentication
#                     # sudo('chmod 700 /home/' + usernameg)
#                     sudo('chmod 755 /home/' + usernameg)
#                     sudo('chmod 755 /home/' + usernameg + '/.ssh')
#                     sudo('chmod 600 /home/' + usernameg + '/.ssh/id_rsa')
#                     sudo('gpasswd -a ' + usernameg + ' wheel')
#             except KeyError:
#                 print colored('####################################', 'blue')
#                 print colored('User ' + usernameg + 'does not exists', 'blue')
#                 print colored('####################################', 'blue')
#
#                 # if user_exists == "" and usernameg != "root":
#                 #     print colored('User ' + usernameg + ' does not exist', 'red')
#                 #     print colored('#######################################################', 'blue')
#                 #     print colored('Consider that we generate user: username pass: username', 'blue')
#                 #     print colored('#######################################################', 'blue')
#                 #
#                 #     sudo('useradd ' + usernameg + ' -m -d /home/' + usernameg)
#                 #     sudo('echo "' + usernameg + ':' + usernameg + '" | chpasswd')
#                 #     sudo("ssh-keygen -t rsa -f /home/" + usernameg + "/.ssh/id_rsa -N ''", user=usernameg)
#                 #     sudo('chmod 755 /home/' + usernameg)
#                 #     sudo('chmod 755 /home/' + usernameg + '/.ssh')
#                 #     sudo('chmod 600 /home/' + usernameg + '/.ssh/id_rsa')
#                 #     sudo('gpasswd -a ' + usernameg + ' wheel')
#
# ug_instance = GenUser()


@task
def gen(usernameg):
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


@task
def read_file(key_file, username):
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


@task
def appending(usernamea):
    """
Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    :param usernamea: "username" to append the key to.
    """
    with settings(warn_only=False):
        if usernamea == "root":
            key_file = '/' + usernamea + '/.ssh/id_rsa.pub'
            key_text = read_file(key_file, usernamea)
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
            key_text = read_file(key_file, usernamea)
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


@task
def append_no_prompt(usernamea):
    """
Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host skiping servers that throws pass
prompt skiping servers that throws pass prompt
    :param usernamea: "username" to append the key to.
    """
    env.abort_on_prompts = True
    try:
        with settings(warn_only=False):
            if usernamea == "root":
                key_file = '/' + usernamea + '/.ssh/id_rsa.pub'
                key_text = read_file(key_file, usernamea)
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
                key_text = read_file(key_file, usernamea)
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
    except SystemExit:
        print colored('######################################################', 'red')
        print colored('"' + usernamea + '" couldnt be created for some reason', 'red')
        print colored('######################################################', 'red')


@task
def remove(usernamea):
    """
Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    :param usernamea: "username" to append the key to.
    """
    with settings(warn_only=False):
        if usernamea == "root":
            key_file = '/' + usernamea + '/.ssh/id_rsa.pub'
            key_text = read_file(key_file, usernamea)
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
            key_text = read_file(key_file, usernamea)
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


@task
def test(usernamet):
    """
Test SSH (authorized_keys) in the host
    :param usernamet: "username" keys to test
    """
    env.abort_on_prompts = True
    try:
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
            # [ntorres@jumphost fabric]$ ssh -i /home/ntorres/.ssh/id_rsa ntorres@10.0.3.113  Warning: Permanently added
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
                    'ssh -i ~/temp/id_rsa -o "StrictHostKeyChecking no" -q ' + usernamet + '@' + env.host_string +
                    ' exit')
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

    except SystemExit:
        print colored('###################################################', 'red')
        print colored(usernamet + " FAIL! IP:" + env.host_string, 'red')
        print colored('###################################################', 'red')
