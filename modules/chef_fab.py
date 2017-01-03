# Import Fabric's API module#
from fabric.api import settings
from fabric.contrib.files import exists, run, sudo, cd
from fabric.decorators import task
from termcolor import colored

from modules import file_fab


@task
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


@task
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
            file_fab.send_mod('./conf/chef/knife-zero/knife.rb', '/home/' + usernamek + '/my_chef_repo/', '600')

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
