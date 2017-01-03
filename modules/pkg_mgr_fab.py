# Import Fabric's API module#
from fabric.api import settings, env, sudo
from fabric.decorators import task
from termcolor import colored


@task
def apt_package(action, package):
    """
Install/Upgrade Debian apt based linux package
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


@task
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
