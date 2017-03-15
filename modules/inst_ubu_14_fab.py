# Import Fabric's API module#
from fabric.contrib.files import exists, sed
from fabric.decorators import task
from fabric.api import sudo, settings, run, cd
from termcolor import colored
from modules import file_fab, mysql_fab


@task
def install_postfix_ubuntu_14():
    """
Postfix Internet Mailserver installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('=================================', 'blue')
        print colored('INSTALLING : "Postfix Mailserver"', 'blue')
        print colored('=================================', 'blue')

        sudo('DEBIAN_FRONTEND=noninteractive apt-get -y install postfix mailutils')
        file_fab.send("./conf/UNC/postfix/main.cf", "/etc/postfix/main.cf")
        file_fab.send("./conf/UNC/postfix/virtual", "/etc/postfix/virtual")
        sudo('chown 0:0 /etc/postfix/main.cf')
        sudo('chown 0:0 /etc/postfix/virtual')
        sudo('postmap /etc/postfix/virtual')
        sudo('service postfix restart')
        sudo('netstat -putona | grep 25')
        sudo('cat /var/log/mail.log')


@task
def install_squid_ubuntu_14():
    """
Squid3 HTTP Proxy installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('======================================', 'blue')
        print colored('INSTALLING : "Squid HTTP Proxy Server"', 'blue')
        print colored('======================================', 'blue')

        sudo('apt-get install -y squid apache2-utils')
        file_fab.send("./conf/UNC/squid/squid.conf", "/etc/squid3/squid.conf")
        file_fab.send("./conf/UNC/squid/squid_passwd", "/etc/squid3/squid_passwd")
        file_fab.send("./conf/UNC/squid/restricted-sites.squid", "/etc/squid3/restricted-sites.squid")
        sudo('chown 0:0 /etc/squid3/squid.conf')
        sudo('chown 0:0 /etc/squid3/squid_passwd')
        sudo('chown 0:0 /etc/squid3/restricted-sites.squid')
        sudo('service squid3 restart')
        sudo('cat /etc/squid3/squid.conf | egrep -v \'^#|^$\'')
        sudo('netstat -putona | grep 3128')
        sudo('cat /var/log/squid3/access.log')


@task
def install_apache24_ubuntu_14():
    """
Apache2 HTTP Server installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('##########################', 'blue')
        print colored('#### APACHE2 WEB_SERV ####', 'blue')
        print colored('##########################', 'blue')
        sudo('apt-get install -y apache2')
        sudo('sh /conf/apache2/gen-cer.sh binbash.com.ar')
        file_fab.send("./conf/UNC/apache2/ports.conf", "/etc/apache2/ports.conf")
        file_fab.send("./conf/UNC/apache2/binbash.com.ar.conf", "/etc/apache2/sites-available/binbash.com.ar.conf")
        sudo('chown 0:0 /etc/apache2/ports.conf')
        sudo('chown 0:0 /etc/apache2/sites-available/binbash.com.ar.conf')
        sudo('mkdir -p /var/www/binbash.com.ar/public_html')
        sudo('mkdir -p /var/www/binbash.com.ar/logs')

        sudo('wget -P /var/www/binbash.com.ar'
             ' --recursive'
             ' --no-clobber'
             ' --page-requisites'
             ' --html-extension'
             ' --convert-links'
             ' --restrict-file-names=windows'
             ' --domains website.org'
             ' --no-parent'
             ' http://www.binbash.com.ar')

        sudo('cp /var/www/binbash.com.ar/www.binbash.com.ar/index.html /var/www/binbash.com.ar/public_html/index.html')
        sudo('rm -r /var/www/binbash.com.ar/www.binbash.com.ar/')
        sudo('echo "ServerName localhost" >> /etc/apache2/apache2.conf')
        sudo('a2ensite binbash.com.ar')
        sudo('chmod -R 755 /var/www')
        sudo('service apache2 restart')


@task
def install_logrotate_ubuntu_14():
    """
Logrotate installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('======================================', 'blue')
        print colored('INSTALLING : "Logrotate Service      "', 'blue')
        print colored('======================================', 'blue')

        sudo('apt-get install -y logrotate')
        file_fab.send("./conf/UNC/logrotate/logrotate.conf", "/etc/logrotate.conf")
        file_fab.send("./conf/UNC/logrotate/squid3", "/etc/logrotate.d/squid3")
        file_fab.send("./conf/UNC/logrotate/apache2", "/etc/logrotate.d/apache2")
        file_fab.send("./conf/UNC/logrotate/postfix", "/etc/logrotate.d/postfix")
        sudo('chown 0:0 /etc/logrotate.conf')
        sudo('chown 0:0 /etc/logrotate.d/squid3')
        sudo('chown 0:0 /etc/logrotate.d/apache2')
        sudo('chown 0:0 /etc/logrotate.d/postfix')


@task
def install_munin_master_ubuntu_14():
    """
Munin Master HTTP Monitoring installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('=======================================', 'blue')
        print colored('INSTALLING : "Munin Monitoring Service"', 'blue')
        print colored('=======================================', 'blue')

        sudo('apt-get install -y apache2 apache2-utils libcgi-fast-perl libwww-perl libapache2-mod-fcgid munin')
        sudo('apt-get install munin-plugins-extra')
        with settings(warn_only=True):
            sudo('a2enmod fcgid')

        file_fab.send("./conf/UNC/munin/munin.conf", "/etc/munin/munin.conf")
        file_fab.send("./conf/UNC/munin/apache.conf", "/etc/munin/apache.conf")
        file_fab.send("./conf/UNC/munin/apache.conf", "/etc/munin/plugin-conf.d/munin-node")
        file_fab.send('chown 0:0 /etc/munin/munin.conf')
        file_fab.send('chown 0:0 /etc/munin/apache.conf')
        file_fab.send('chown 0:0 /etc/munin/plugin-conf.d/munin-node')

        # Activating extra plugins (Apache & Squid)
        with settings(warn_only=True):
            sudo('/usr/sbin/munin-node-configure --suggest')
            sudo('/usr/sbin/munin-node-configure --shell | sudo sh')

        with settings(warn_only=True):
            sudo('ln -s /usr/share/munin/plugins/squid_cache /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_icp /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_objectsize /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_requests /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_traffic /etc/munin/plugins/')

        with settings(warn_only=True):
            sudo('/usr/sbin/munin-node-configure --suggest | egrep \'squid|apache|nfs|postfix|firewall|munin\'')

        # Restarting services

        sudo('service apache2 restart')
        sudo('service munin-node restart')


@task
def install_munin_node_ubuntu_14():
    """
Munin Node HTTP Monitoring installation in Ubuntu 14.04.
    """
    with settings(warn_only=False):
        print colored('=======================================', 'blue')
        print colored('INSTALLING : "Munin Monitoring Service"', 'blue')
        print colored('=======================================', 'blue')

        sudo('apt-get install -y munin-node libwww-perl')
        sudo('apt-get install munin-plugins-extra')
        file_fab.send("./conf/UNC/munin/munin-node.conf", "/etc/munin/munin-node.conf")
        sudo('chown 0:0 /etc/munin/munin-node.conf')

        # Activating extra plugins (Apache & Squid)
        with settings(warn_only=True):
            sudo('/usr/sbin/munin-node-configure --suggest')
            sudo('/usr/sbin/munin-node-configure --shell | sudo sh')
            sudo('ln -s /usr/share/munin/plugins/squid_cache /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_icp /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_objectsize /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_requests /etc/munin/plugins/')
            sudo('ln -s /usr/share/munin/plugins/squid_traffic /etc/munin/plugins/')
            sudo('/usr/sbin/munin-node-configure --suggest | egrep \'squid|apache|nfs|postfix|firewall|munin\'')

        # Restarting services
        sudo('service munin-node restart')


@task
def install_jenkins():
    """
Install Jenkins Server w/ prerequisites

    """
    with settings(warn_only=False):
        print colored('===================================================================', 'blue')
        print colored('DEPENDENCIES PROVISIONING                          ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        run('wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | sudo apt-key add -')
        sudo('sh -c \'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list\'')
        sudo('apt-get update')
        sudo('apt-get install -y git jenkins redis-tools mysql-client pigz rsync')
        file_fab.send("./conf/rsync/rsync-no24.sh", "/usr/bin/rsync-no24")

        # /var/lib/jenkins/job
        # /var/lib/jenkins/users
        # ssh keys /var/lib/jenkins/.ssh/id_rsa
        # ssh keys /var/lib/jenkins/.ssh/id_rsa_bitbucket
        # ssh keys /var/lib/jenkins/.ssh/kwnon_hosts
        # pip packages for deployments

        # Jenkins Plugins:
        # Role-based Authorization Strategy => /var/lib/jenkins/config.xml => here are the roles
        # Slack Notification Plugin
        # Extensible choice parameter
        # Multiple SCMs
        # SCM Sync Configuration Plugin
        # Last Changes Plugin
        # Bitbucket Branch Source Plugin
        # Checkstyle (for processing PHP_CodeSniffer logfiles in Checkstyle format)
        # Clover PHP (for processing PHPUnit's Clover XML logfile)
        # DRY Plug-in (for processing phpcpd logfiles in PMD-CPD format) => Depends on Static Analysis Utilities plugin
        # Bitbucket pullrequest builder plugin - to support it as code then => "Job DSL plugin"


@task
def install_upgrade_python_27_13():
    """
Install and upgrade python 2.7 to Python 2.7.13

    """
    with settings(warn_only=False):
        print colored('===================================================================', 'blue')
        print colored('DEPENDENCIES PROVISIONING                          ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        sudo('apt-get install -y build-essential checkinstall')
        sudo('apt-get install -y libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev '
             'tk-dev libgdbm-dev libc6-dev libbz2-dev')

        with cd('/usr/src'):
            if exists('./Python-2.7.13.tgz', use_sudo=True):
                if exists('./Python-2.7.13', use_sudo=True):
                    with cd('/usr/src/Python-2.7.13'):
                        sudo('./configure')
                        sudo('make altinstall')
                else:
                    sudo('tar xzf Python-2.7.13.tgz')
                    with cd('/usr/src/Python-2.7.13'):
                        sudo('./configure')
                        sudo('make altinstall')
            else:
                sudo('wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz')
                sudo('tar xzf Python-2.7.13.tgz')
                with cd('/usr/src/Python-2.7.13'):
                    sudo('./configure')
                    sudo('make altinstall')

        python_ver = run('python2.7 -V')
        if python_ver == "Python 2.7.13":
            print colored('==========================', 'blue')
            print colored('Python SUCCESFULLY UPDATED', 'blue', attrs=['bold'])
            print colored('==========================', 'blue')
        else:
            print colored('================================', 'blue')
            print colored('Python NOT UPDATED, please check', 'blue', attrs=['bold'])
            print colored('================================', 'blue')

        with cd('/usr/bin'):
            sudo('ls -ltra | grep python')
            sudo('rm python')
            sudo('ln -s /usr/src/Python-2.7.13/python python')
            sudo('ls -ltra | grep python')

        pip_status = str(run('pip | grep "pip <command>"'))
        pip_status = pip_status.strip()
        if pip_status != "pip <command> [options]":
            with cd('/usr/src'):
                sudo('wget https://bootstrap.pypa.io/get-pip.py')
                sudo('python get-pip.py')
                sudo('pip install --upgrade pip')


@task
def install_docker(username):
    """
Install Docker Engine, docker-compose, docker-machine
    :param username: user to be aded to the docker group
    """
    with settings(warn_only=False):

        print colored('################################################################', 'red', attrs=['bold'])
        print colored('################################################################', 'red', attrs=['bold'])

        print colored(' ____             _               ____                           ', 'blue', attrs=['bold'])
        print colored('|  _ \  ___   ___| | _____ _ __  / ___|  ___ _ ____   _____ _ __ ', 'blue', attrs=['bold'])
        print colored('| | | |/ _ \ / __| |/ / _ \  __| \___ \ / _ \  __\ \ / / _ \  __|', 'blue', attrs=['bold'])
        print colored('| |_| | (_) | (__|   <  __/ |     ___) |  __/ |   \ V /  __/ |   ', 'blue', attrs=['bold'])
        print colored('|____/ \___/ \___|_|\_\___|_|    |____/ \___|_|    \_/ \___|_|   ', 'blue', attrs=['bold'])

        print colored('                                                                  ', 'blue')
        print colored('                                                                  ', 'blue')

        print colored('                                 xMMMMMMc', 'cyan')
        print colored('                                 xMMMMMMc', 'cyan')
        print colored('                                 xMMMMMMc', 'cyan')
        print colored('                  ......  ...... ;dddddd ', 'cyan')
        print colored('                 oWWWWWWo0NNNNNN,dNNNNNN:                     dOl.', 'cyan')
        print colored('                 dMMMMMMdXMMMMMM,xMMMMMMc                    kMMMWd.', 'cyan')
        print colored('                 dMMMMMMdXMMMMMM,xMMMMMMc                   cMMMMMMO.', 'cyan')
        print colored('                ,,,,,, :xxxxxx;oxxxxxx.:xxxxxx .,,,,,,.           xMMMMMMMO. ....', 'cyan')
        print colored('                .XMMMMMW,dMMMMMMdXMMMMMM,xMMMMMMckMMMMMMc           lMMMMMMMMXNWMWWX0x:.',
                      'cyan')
        print colored('        .XMMMMMW,dMMMMMMdXMMMMMM,dMMMMMMckMMMMMMc           .0MMMMMMMMMMMMMMMMK.', 'cyan')
        print colored('        .XMMMMMW,dMMMMMMdXMMMMMM,xMMMMMMckMMMMMMc            ;NMMMMMMMMMMMMMWk.', 'cyan')
        print colored(',;;;;;;:dddddddclddddddloddddddclddddddcoddddddl;;;;;;:cldOKWMMMMMMMMMWXOdc.', 'cyan')
        print colored('WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWc''..', 'cyan')
        print colored('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNc', 'cyan')
        print colored('WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN;', 'cyan')
        print colored('0MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMO.', 'cyan')
        print colored(':WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMd', 'cyan')
        print colored(' dMMMMMMMMMMMMMMMMMMW0KxKMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM0:', 'cyan')
        print colored('  dMMMMMMMMMMMMMMMMMNOKO0MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNx,', 'cyan')
        print colored('   oWMMMMMMMMMWWX0ONMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWx.', 'cyan')
        print colored('    .d0o .......    0MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNOc.', 'cyan')
        print colored('      .dOl.          lNMMMMMMMMMMMMMMMMMMMMMMMMMNOc.', 'cyan')
        print colored('        .:odo:.       .lKWMMMMMMMMMMMMMMMMMWKxc,.', 'cyan')
        print colored('            .;dxxxoc:;, .ckXMMMMMMMMWX0xo: .', 'cyan')
        print colored('                     cxOKNWWWWWWNXKOxo; .', 'cyan')

        print colored('                                                                  ', 'blue')
        print colored('                                                                  ', 'blue')

        print colored('              cd.                                ,dc', 'blue')
        print colored('              XMo                                kMW.', 'blue')
        print colored('     .,:cc: . XMo     .;ccc;.           :ccc;.   kMW.   ;;       :llc;.         . ;:,', 'blue')
        print colored('   c0WW0OOKWW0WMo  .dXMN0OOXMNx.    ,OWWKOO0NW:  kMW..dNMO   ,OWMKOk0NMKl.    :0WWK0x', 'blue')
        print colored('  OMXc     .cXMMo  NMO,      xWN;  oMNo.         kMWONWk,   oWNl.     xMMK  .0MK:.', 'blue')
        print colored(' cMW         .WMo OMk         oMN.,MM:           kMMWx.    ;MM;    .lKM0l.  dMX.', 'blue')
        print colored(' cMN.        .NMl 0Mx         lMW.,MM,           kMMWl     :MM,  ,OWM0;     kM0', 'blue')
        print colored(' .KMO'      '0MK. :WWo.      cNMd  xMK;          kMMXMXl.   xMKl0WXd        kM0', 'blue')
        print colored('  .xWMKdooxKMWd.   ,0MWOdlokNMX:    lNMNkdodOK;  kMW.;0MNo   cXMMNxoxOK:    kM0', 'blue')
        print colored('    .;ldxxdl,        .:oxxxo:.        ,ldxxdo;   ,dl    do      cdxxxo;     ;x:', 'blue')

        print colored('                                                                  ', 'blue')
        print colored('                                                                  ', 'blue')

        print colored('===================================================================', 'blue')
        print colored('DEPENDENCIES PROVISIONING                          ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        sudo('apt-get update')
        sudo('apt-get install -y --no-install-recommends linux-image-extra-$(uname -r) linux-image-extra-virtual')

        print colored('===================================================================', 'blue')
        print colored('INSTALLING PYTHON PIP                              ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        sudo('apt-get install -y python-pip')
        sudo('pip install --upgrade pip')

        print colored('===================================================================', 'blue')
        print colored('DOCKER ENGINE PROVISIONING                         ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')

        with settings(warn_only=True):
            docker_version = run('docker -v')
            docker_version.strip()
            if "Docker version" not in docker_version:
                # Set up the repository.
                sudo('apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl'
                     ' software-properties-common')
                run('curl -fsSL https://apt.dockerproject.org/gpg | sudo apt-key add -')
                sudo('add-apt-repository "deb https://apt.dockerproject.org/repo/ ubuntu-$(lsb_release -cs) main"')

                # Install Docker
                sudo('apt-get update')
                sudo('apt-get -y install docker-engine')
            else:
                print colored('===================================================================', 'blue')
                print colored('DOCKER ' + docker_version + ' INSTALLED          ', 'blue', attrs=['bold'])
                print colored('===================================================================', 'blue')

        # Verify docker is installed correctly by running a test image in a container.
        sudo('docker run --rm hello-world')

        # The docker daemon binds to a Unix socket instead of a TCP port.
        # By default that Unix socket is owned by the user root and other users can access it with sudo.
        # For this reason, docker daemon always runs as the root user.
        # To avoid having to use sudo when you use the docker command, create a Unix group called
        # docker and add users to it. When the docker daemon starts, it makes the ownership of
        # the Unix socket read/writable by the docker group. Uncoment the sudo() lines below if you like
        # to achieve this result
        with settings(warn_only=True):
            # Add your user to docker group.
            sudo('usermod -aG docker ' + username)

        print colored('===================================================================', 'blue')
        print colored('DOCKER COMPOSE PROVISIONING                         ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')

        sudo('pip install docker-compose')

        print colored('===================================================================', 'blue')
        print colored('DOCKER MACHINE PROVISIONING                         ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')

        with settings(warn_only=True):
            docker_machine_version = run('docker-machine -v')
            print colored(docker_machine_version, 'red', attrs=['bold'])
            docker_machine_version.strip()
            if "docker-machine version" not in docker_machine_version:
                # Run the Docker installation script.
                sudo('curl -L https://github.com/docker/machine/releases/download/'
                     'v0.9.0/docker-machine-`uname -s`-`uname -m` >/tmp/docker-machine && '
                     'chmod +x /tmp/docker-machine && '
                     'sudo cp /tmp/docker-machine /usr/local/bin/docker-machine')

            else:
                print colored('===================================================================', 'blue')
                print colored('DOCKER ' + docker_machine_version + ' INSTALLED     ', 'blue', attrs=['bold'])
                print colored('===================================================================', 'blue')

        run('docker -v && docker-compose -v && docker-machine -v')


@task
def install_wordpress():
    """
Install wordpress CMS on Ubuntu 14.04

    """
    with settings(warn_only=False):
        print colored('===================================================================', 'blue')
        print colored('DEPENDENCIES PROVISIONING                          ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        sudo('apt-get install unzip')

        sudo('mkdir -p /var/www/html')
        with cd('/var/www/html'):
            if exists('./latest.zip', use_sudo=True):
                if exists('./wordpress', use_sudo=True):
                    print colored('==========================================', 'yellow')
                    print colored('WORDPRESS alredy INSTALLED', 'yellow', attrs=['bold'])
                    print colored('==========================================', 'yellow')
                else:
                    sudo('unzip latest.zip')
                    sudo('rm -rf ./latest.zip')
                    if exists('./wordpress', use_sudo=True):
                        print colored('======================================', 'blue')
                        print colored('WORDPRESS INSTALLED OK', 'blue', attrs=['bold'])
                        print colored('======================================', 'blue')

            else:
                sudo('wget https://wordpress.org/latest.zip')
                sudo('unzip latest.zip')
                sudo('rm -rf ./latest.zip')
                if exists('./wordpress', use_sudo=True):
                    print colored('======================================', 'blue')
                    print colored('WORDPRESS INSTALLED OK', 'blue', attrs=['bold'])
                    print colored('======================================', 'blue')

        sudo('apt-get install -y apache2 mysql-server')
        sudo('apt-get install -y php5 libapache2-mod-php5 php5-mcrypt php5-mysql')

        sudo('chown -R www-data:www-data /var/www/html/*')
        file_fab.send("./conf/apache/wordpress.conf", "/etc/apache2/sites-available/wordpress.conf")
        file_fab.send("./conf/php/wordpress_php.ini", "/etc/php5/apache2/php.ini")
        sudo('sudo a2dissite 000-default.conf')
        sudo('sudo a2ensite wordpress')
        sudo('service apache2 reload')
        sudo('service apache2 restart')

        sudo('chmod 757 /etc/apache2/mods-available/')
        sudo('chmod 666 /etc/apache2/mods-available/dir.conf')
        str_to_remove = "DirectoryIndex index.html index.cgi index.pl index.php index.xhtml index.htm"
        str_to_add = "DirectoryIndex index.php index.html index.cgi index.pl index.php index.xhtml index.htm"
        sed('/etc/apache2/mods-enabled/dir.conf', str_to_remove, str_to_add, limit='', use_sudo=True, backup='.bak', flags='',
            shell=False)
        sudo('chmod 755 /etc/apache2/mods-available/')
        sudo('chmod 644 /etc/apache2/mods-available/dir.conf')
        sudo('service apache2 restart')

        mysql_fab.create_db("wp_binbash_db","root")
        mysql_fab.create_local_user("root", "wp_binbash_user", db_user_pass="wp_binbash_pass")
        mysql_fab.grant_user_db("wp_binbash_db", "wp_binbash_user", db_user_pass="wp_binbash_pass")


@task
def local_env(username):
    """
Install wordpress CMS on Ubuntu 14.04

    """
    with settings(warn_only=False):
        print colored('===================================================================', 'blue')
        print colored('DEPENDENCIES PROVISIONING                          ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')

        print colored('===================================================================', 'blue')
        print colored('INSTALLING ORACLE JAVA 1.8.0', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        # add conditonal to validate java version
        # vagrant@jwt:/data$ java -version
        # java version "1.8.0_121"
        # Java(TM) SE Runtime Environment (build 1.8.0_121-b13)
        # Java HotSpot(TM) 64-Bit Server VM (build 25.121-b13, mixed mode)
        # vagrant@jwt:~$ sudo update-alternatives --config java
        # There are 2 choices for the alternative java (providing /usr/bin/java).
        # Selection    Path                                            Priority   Status
        # ------------------------------------------------------------
        #  0            /usr/lib/jvm/java-8-oracle/jre/bin/java          1081      auto mode
        #  1            /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java   1071      manual mode
        #* 2            /usr/lib/jvm/java-8-oracle/jre/bin/java          1081      manual mode
        #sudo('update-alternatives --config java')
        java_version = run('java -version')
        java_version.strip()
        print "CURRENT JAVA VER: " + java_version
        if "1.8.0" not in java_version:
            # Set up the repository.
            sudo('add-apt-repository ppa:webupd8team/java')
            sudo('apt-get update')
            sudo('apt-get install oracle-java8-installer')

        else:
            print colored('===============================================================', 'blue')
            print colored('JAVA VERSION: ' + java_version + ' INSTALLED   ', 'blue', attrs=['bold'])
            print colored('===============================================================', 'blue')


        print colored('================================', 'blue')
        print colored('INSTALLING MAVEN', 'blue', attrs=['bold'])
        print colored('================================', 'blue')
        # Java dependencies
        # Upgrade to MAVEN 3.3.9 (http://javedmandary.blogspot.com.ar/2016/09/install-maven-339-on-ubuntu.html)
        # vagrant@jwt:/data$ mvn -version
        # Apache Maven 3.0.5
        # Maven home: /usr/share/maven
        # Java version: 1.8.0_121, vendor: Oracle Corporation
        # Java home: /usr/lib/jvm/java-8-oracle/jre
        # Default locale: en_US, platform encoding: ANSI_X3.4-1968
        # OS name: "linux", version: "3.13.0-112-generic", arch: "amd64", family: "unix"
        # sudo('apt-get install maven')
        maven_version = run('mvn -version')
        maven_version.strip()
        print "CURRENT MAVEN VER: " + maven_version

        if "3.3.9" not in maven_version:
            with cd('/home/' + username):
                if exists('/home/' + username + '/apache-maven-3.3.9-bin.tar.gz', use_sudo=True):
                    if exists('/usr/local/apache-maven', use_sudo=True):
                        sudo('mv apache-maven-3.3.9-bin.tar.gz /usr/local/apache-maven')
                        with cd('/usr/local/apache-maven'):
                            sudo('tar -xzvf apache-maven-3.3.9-bin.tar.gz')
                            run('export M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9')
                            run('export M2=$M2_HOME/bin')
                            run('export MAVEN_OPTS="-Xms256m -Xmx512m"')
                            run('export PATH=$M2:$PATH')

                            run('echo "M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9" >> ~/.bashrc')
                            run('echo "M2=$M2_HOME/bin" >> ~/.bashrc')
                            run('echo "MAVEN_OPTS=\"-Xms256m -Xmx512m\"" >> ~/.bashrc')
                            run('echo "PATH=$M2:$PATH" >> ~/.bashrc')

                else:
                    run('wget http://apache.mirrors.lucidnetworks.net/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz')
                    if exists('/usr/local/apache-maven', use_sudo=True):
                        sudo('mv apache-maven-3.3.9-bin.tar.gz /usr/local/apache-maven')
                        with cd('/usr/local/apache-maven'):
                            sudo('tar -xzvf apache-maven-3.3.9-bin.tar.gz')
                            run('export M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9')
                            run('export M2=$M2_HOME/bin')
                            run('export MAVEN_OPTS="-Xms256m -Xmx512m"')
                            run('export PATH=$M2:$PATH')

                            run('echo "M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9" >> ~/.bashrc')
                            run('echo "M2=$M2_HOME/bin" >> ~/.bashrc')
                            run('echo "MAVEN_OPTS=\"-Xms256m -Xmx512m\"" >> ~/.bashrc')
                            run('echo "PATH=$M2:$PATH" >> ~/.bashrc')

                    else:
                        sudo('mkdir -p /usr/local/apache-maven')
                        sudo('mv apache-maven-3.3.9-bin.tar.gz /usr/local/apache-maven')
                        with cd('/usr/local/apache-maven'):
                            sudo('tar -xzvf apache-maven-3.3.9-bin.tar.gz')
                            run('export M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9')
                            run('export M2=$M2_HOME/bin')
                            run('export MAVEN_OPTS="-Xms256m -Xmx512m"')
                            run('export PATH=$M2:$PATH')

                            run('echo "M2_HOME=/usr/local/apache-maven/apache-maven-3.3.9" >> ~/.bashrc')
                            run('echo "M2=$M2_HOME/bin" >> ~/.bashrc')
                            run('echo "MAVEN_OPTS=\"-Xms256m -Xmx512m\"" >> ~/.bashrc')
                            run('echo "PATH=$M2:$PATH" >> ~/.bashrc')

            maven_final_ver = run('mvn -version')
            print colored('============================================', 'blue')
            print colored('MAVEN VERSION: ' + maven_final_ver , 'blue', attrs=['bold'])
            print colored('============================================', 'blue')

        else:
            print colored('==========================================================', 'blue')
            print colored('MAVEN VERSION up to date: ' + maven_version, 'blue', attrs=['bold'])
            print colored('==========================================================', 'blue')

        # NodeJs
        node_version = run('node -v')
        node_version.strip()
        print "CURRENT NODE VER: " + node_version
        if "7.6.0" not in node_version:
            sudo('apt-get install node nodejs npm')
            sudo('npm cache clean -f')
            sudo('npm install -g n')
            sudo('n stable')

        else:
            print colored('===============================================================', 'blue')
            print colored('NODE VERSION: ' + node_version + ' INSTALLED   ', 'blue', attrs=['bold'])
            print colored('===============================================================', 'blue')


        # Python
        sudo('apt-get install python-tk')
        sudo('pip install scipy')
        sudo('pip install matplotlib')
        sudo('pip install pytrends')


        # vagrant@jwt:/data$ mvn clean package -P development
        # vagrant@jwt:/data$ mvn -DskipTests clean package -P development
        # npm install -g grunt-cli

        # 332 -rw-rw-r-- 1 vagrant vagrant 338245 Mar 14 19:51 frontend.zip
        # vagrant@jwt:/data/jwt-cic-frontend/target$ pwd
        # /data/jwt-cic-frontend/target

        # vagrant@jwt:/data/jwt-cic-services$ cd target/
        # vagrant@jwt:/data/jwt-cic-services/target$ java -jar jwt-cic-services-0.0.1-SNAPSHOT.jar &

        vagrant@jwt:/data/jwt-cic-frontend$ pwd
        /data/jwt-cic-frontend
        vagrant@jwt:/data/jwt-cic-frontend$ grunt serve
        vagrant@jwt:/data/jwt-cic-frontend$ npm run serve

        > jwt-cic-frontend@0.0.1 serve /data/jwt-cic-frontend
        > grunt serve

        npm ERR! weird error 1
        npm WARN This failure might be due to the use of legacy binary "node"
        npm WARN For further explanations, please read
        /usr/share/doc/nodejs/README.Debian

        npm ERR! not ok code 0



        # Not necesary sudo ln -sf /usr/local/n/versions/node/<VERSION>/bin/node /usr/bin/node

        # aclarar el tema del S3.