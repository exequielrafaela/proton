# Import Fabric's API module#
from fabric.api import sudo, settings, env, run, local, put, cd, get, hide
from fabric.decorators import task
from termcolor import colored


@task
def add_centos_sudo(usernamec):
    """
Add a user in RedHat/Centos based OS in wheel group (sudo)
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
                print colored('##############################', 'red')
                print colored('"' + usernamec + '" already exists', 'red')
                print colored('##############################', 'red')
                sudo('gpasswd -a ' + usernamec + ' wheel')
            else:
                print colored('#################################', 'blue')
                print colored('"' + usernamec + '" doesnt exists', 'blue')
                print colored('WILL BE CREATED', 'blue')
                print colored('##################################', 'blue')
                sudo('useradd ' + usernamec + ' -m -d /home/' + usernamec)
                # sudo('echo "' + usernamec + ':' + usernamec + '" | chpasswd')
                sudo('gpasswd -a ' + usernamec + ' wheel')
        except SystemExit:
            # else:
            print colored('######################################################', 'red')
            print colored('"' + usernamec + '" couldnt be created for some reason', 'red')
            print colored('######################################################', 'red')


@task
def add_centos_sudo_no_prompt(usernamec):
    """
Add a user in RedHat/Centos based OS in wheel group (sudo) skiping servers that throws pass prompt
    :param usernamec: "username" to add
    """
    env.abort_on_prompts = True
    try:
        with settings(warn_only=True):
            try:
                user_true = sudo('cut -d: -f1 /etc/passwd | grep ' + usernamec)
                if user_true != "":
                    print colored('##############################', 'red')
                    print colored('"' + usernamec + '" already exists', 'red')
                    print colored('##############################', 'red')
                    sudo('gpasswd -a ' + usernamec + ' wheel')
                else:
                    print colored('#################################', 'blue')
                    print colored('"' + usernamec + '" doesnt exists', 'blue')
                    print colored('WILL BE CREATED', 'blue')
                    print colored('##################################', 'blue')
                    sudo('useradd ' + usernamec + ' -m -d /home/' + usernamec)
                    # sudo('echo "' + usernamec + ':' + usernamec + '" | chpasswd')
                    sudo('gpasswd -a ' + usernamec + ' wheel')
            except SystemExit:
                print colored('######################################################', 'red')
                print colored('"' + usernamec + '" couldnt be created for some reason', 'red')
                print colored('######################################################', 'red')
    except SystemExit:
        print colored('######################################################', 'red')
        print colored('"' + usernamec + '" couldnt be created for some reason', 'red')
        print colored('######################################################', 'red')


@task
def add_centos(usernamec):
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

            else:
                print colored('#################################', 'green')
                print colored('"' + usernamec + '" doesnt exists', 'green')
                print colored('WILL BE CREATED', 'green')
                print colored('##################################', 'green')
                sudo('useradd ' + usernamec + ' -m -d /home/' + usernamec)

        except SystemExit:
            # else:
            print colored('######################################################', 'green')
            print colored('"' + usernamec + '" couldnt be created for some reason', 'green')
            print colored('######################################################', 'green')


@task
def add_ubuntu(usernamec):
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


@task
def remove_from_group_centos(usernamelist, group):
    """
Remove a user from a certain group in RedHat/Centos based OS
    :param usernamelist: "username" list to add
    :param group: "group" where the user is going to be romoved

eg: fab -f fabfile.py user_remove_from_group_centos:'tom;dick;harry',wheel
    """
    with settings(warn_only=True):
        try:
            if isinstance(usernamelist, basestring):
                usernamelist = usernamelist.split(";")
            for usern in usernamelist:
                user_true = sudo('cut -d: -f1 /etc/passwd | grep ' + usern)
                if user_true != "":
                    print colored('##################################################', 'green')
                    print colored('"' + usern + 'will be removed from gorup ' + group, 'green')
                    print colored('##################################################', 'green')
                    sudo('gpasswd -d ' + usern + ' ' + group)
                else:
                    print colored('#################################', 'green')
                    print colored('"' + usern + '" doesnt exists', 'green')
                    print colored('NOT possible to remove it', 'green')
                    print colored('##################################', 'green')

        except SystemExit:
            # else:
            print colored('######################################################', 'green')
            print colored('"' + usernamelist + '" couldnt be removed for some reason', 'green')
            print colored('######################################################', 'green')


@task
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
