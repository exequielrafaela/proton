# Import Fabric's API module#
from fabric.api import settings
from fabric.decorators import task
from fabric.operations import sudo
from termcolor import colored

from modules import file_fab


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
