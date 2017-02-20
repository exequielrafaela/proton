# Import Fabric's API module#
from fabric.api import settings
from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import sudo, run
from termcolor import colored


@task
def install_ruby():
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


@task
def install_lamp():
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


@task
def install_mysql_server():
    """
MySQL Server installation in Centos7 OS.
    """
    with settings(warn_only=False):
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


@task
def install_various():
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
        sudo('yum clean all')
        sudo('yum install -y epel-release python-devel')

        print colored('===================================================================', 'blue')
        print colored('INSTALLING PYTHON PIP                              ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')
        sudo('yum install -y python-pip')
        sudo('pip install --upgrade pip')

        print colored('===================================================================', 'blue')
        print colored('DOCKER ENGINE PROVISIONING                         ', 'blue', attrs=['bold'])
        print colored('===================================================================', 'blue')

        with settings(warn_only=True):
            docker_version = run('docker -v')
            docker_version.strip()
            if "Docker version" not in docker_version:
                # Run the Docker installation script.
                sudo('curl -fsSL https://get.docker.com/ | sh')
            else:
                print colored('===================================================================', 'blue')
                print colored('DOCKER ' + docker_version + ' INSTALLED          ', 'blue', attrs=['bold'])
                print colored('===================================================================', 'blue')

        # Enable the service.
        sudo('systemctl enable docker.service')
        # Start the Docker daemon.
        sudo('systemctl start docker')
        # Verify docker is installed correctly by running a test image in a container.
        sudo('docker run --rm hello-world')
        # Configure the Docker daemon to start automatically when the host starts:
        sudo('systemctl enable docker')

        # The docker daemon binds to a Unix socket instead of a TCP port.
        # By default that Unix socket is owned by the user root and other users can access it with sudo.
        # For this reason, docker daemon always runs as the root user.
        # To avoid having to use sudo when you use the docker command, create a Unix group called
        # docker and add users to it. When the docker daemon starts, it makes the ownership of
        # the Unix socket read/writable by the docker group. Uncoment the sudo() lines below if you like
        # to achieve this result
        with settings(warn_only=True):
            # Create the docker group
            sudo('groupadd docker')
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
                sudo('curl -L https://github.com/docker/machine/releases/download/v0.8.2/'
                     'docker-machine-`uname -s`-`uname -m` '
                     '>/usr/local/bin/docker-machine && chmod +x /usr/local/bin/docker-machine')
            else:
                print colored('===================================================================', 'blue')
                print colored('DOCKER ' + docker_machine_version + ' INSTALLED     ', 'blue', attrs=['bold'])
                print colored('===================================================================', 'blue')


@task
def install_php53():
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
