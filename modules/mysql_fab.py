# Import Fabric's API module#
import os
from time import strftime, gmtime

from fabric.contrib.files import exists
from fabric.api import sudo, settings, cd, get, hide, env

from fabric.decorators import task
from termcolor import colored

from modules import conf_files_fab, passwd_fab, file_fab
import config


@task
def install_client_centos7():
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


@task
def sh_db_user(mysql_user, mysql_ip="127.0.0.1"):
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


@task
def create_db(db_name, admin_db_user, mysql_ip="127.0.0.1"):
    """
Create a MySQL Database with the given db_name
    :param admin_db_user: mysql root user
    :param db_name: Database name to be created
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u ' + admin_db_user + ' -p -e "CREATE DATABASE ' + db_name + ';"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + admin_db_user + ' -p -e "show databases;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


@task
def create_local_user(admin_user, db_user, db_user_pass="password", mysql_ip="127.0.0.1"):
    """
Create a localhost MySQL user
    :param admin_user: MySQL admin user
    :param db_user: Username to be created
    :param db_user_pass: Password for the new username
    :param mysql_ip: MySQL Server IP Address
    """
    with settings(warn_only=False):
        try:
            sudo('mysql -h ' + mysql_ip + ' -u ' + admin_user + ' -p -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + admin_user + ' -p -e "CREATE USER ' + db_user +
                 '@localhost IDENTIFIED BY\'' + db_user_pass + '\';"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + admin_user + ' -p -e "SELECT User, Host, Password FROM mysql.user;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


@task
def grant_user_db(db_name, db_user, db_user_pass="db_user", mysql_ip="127.0.0.1"):
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
            sudo('mysql -h ' + mysql_ip + ' -u root -p -e "FLUSH PRIVILEGES;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


@task
def grant_user_db_rds_with_conf(db_name):
    """
Given the username, grant MySQL permissions for a certain DB to this username
    :param db_name: Database name to grant permissions in
    """
    with settings(warn_only=False):

        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        db_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "db_user")
        # mysql_user_password_enc = \
        #    str(load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "db_user_password"))
        # db_user_pass = base64_decode(mysql_user_password_enc)

        try:
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                 ' -e "SELECT User, Host, Password FROM mysql.user;"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                 ' -e "GRANT ALL ON ' + db_name + '.* TO ' + db_user + '@\'%\';"')
            sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                 ' -e "SELECT User, Host, Password FROM mysql.user;"')
        except SystemExit:
            print colored('===================', 'red')
            print colored('MySQL query problem', 'red')
            print colored('===================', 'red')


@task
def grant_remote_cx(mysql_pass, remote_ip, mysql_ip="127.0.0.1"):
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


@task
def backup_all(local_dir, remote_dir, mysql_user, mysql_ip="127.0.0.1"):
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


@task
def restore_upgrade_all(mysqldump_fname, local_dir, remote_dir, mysql_user, mysql_ip="127.0.0.1"):
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
                file_fab.send_oldmod(local_dir + mysqldump_fname, remote_dir + mysqldump_fname)
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p < ' + remote_dir + mysqldump_fname)
                sudo('mysql_upgrade -h ' + mysql_ip + ' -u ' + mysql_user + ' -p')
                sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p -e "show databases;"')
        else:
            print colored('===================================================', 'red')
            print colored('Check that DIRs: ' + local_dir + mysqldump_fname + ' do exist', 'red')
            print colored('===================================================', 'red')


@task
def backup_db(local_dir, remote_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
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


@task
def backup_db_from_conf(local_dir, remote_dir, db_name, mysql_ip="127.0.0.1"):
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
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)

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


@task
def backup_db_rds(local_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
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


@task
def backup_db_rds_from_conf(local_dir, db_name):
    """
MySQLdump backup for a certain DB passed as argument
fab -R local mysql_backup:/tmp/,testdb
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Server DB name to be backuped

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isdir(local_dir):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

                    if database == db_name:
                        sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                             ' -u ' + mysql_user + ' -p' + password + ' ' + db_name + ' > '
                             + local_dir + db_name + '-bak-' + date + '.sql')
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


@task
def backup_db_rds_from_conf_ggcc_stg(local_dir, db_name):
    """
MySQLdump backup for a certain DB passed as argument
fab -R local mysql_backup:/tmp/,testdb
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Server DB name to be backuped

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isdir(local_dir):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

                    if database == db_name:
                        sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                             ' -u ' + mysql_user + ' -p' + password + ' ' + db_name + ' > '
                             + local_dir + db_name + '-bak-' + date + '.sql')
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


@task
def backup_db_rds_from_conf_ggcc_prd(local_dir, db_name):
    """
MySQLdump backup for a certain DB passed as argument
fab -R local mysql_backup:/tmp/,testdb
NOTE: Consider that the role after -R hast to be the remote MySQL Server.
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Server DB name to be backuped

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_prd", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        date = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isdir(local_dir):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

                    if database == db_name:
                        sudo('mysqldump -q -c --routines --triggers --single-transaction -h ' + mysql_ip +
                             ' -u ' + mysql_user + ' -p' + password + ' ' + db_name + ' > '
                             + local_dir + db_name + '-bak-' + date + '.sql')
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


@task
def restore_to_new_db(mysqldump_fname, local_dir, remote_dir, mysql_user, db_name, mysql_ip="127.0.0.1"):
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
                file_fab.send_oldmod(local_dir + mysqldump_fname, remote_dir + mysqldump_fname)
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


@task
def restore_rds_to_new_db_from_conf(mysqldump_fname, local_dir, db_name):
    """
MySQLdump restore
eg: fab -R local mysql_restore_rds_to_new_db:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,testdb
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Database name to be restored

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        date = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isfile(local_dir + mysqldump_fname):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

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


@task
def restore_rds_to_new_db_from_conf_ggcc_stg(mysqldump_fname, local_dir, db_name):
    """
MySQLdump restore
eg: fab -R local mysql_restore_rds_to_new_db:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,testdb
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Database name to be restored

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isfile(local_dir + mysqldump_fname):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

                    # if database != "" and db_name in database:
                    if database == db_name:
                        sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password + ' '
                             + db_name + ' < ' + local_dir + mysqldump_fname)
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


@task
def restore_rds_to_new_db_from_conf_ggcc_stg_back(mysqldump_fname, local_dir, db_name):
    """
MySQLdump restore
eg: fab -R local mysql_restore_rds_to_new_db:backup-2016-10-04-16-13-10-172.28.128.4.sql,/tmp/,testdb
    :param mysqldump_fname: mysqldump file name to be restored
    :param local_dir: mysqldump jumphost/bastion destination directory
    :param db_name: MySQL Database name to be restored

    """
    with settings(warn_only=False):
        mysql_ip = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "host")
        mysql_user = conf_files_fab.load_configuration(config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "admin_user")
        mysql_password_enc = str(conf_files_fab.load_configuration
                                 (config.MYSQL_CONFIG_FILE_PATH, "mysql_stg", "password"))
        password = passwd_fab.base64_decode(mysql_password_enc)
        date = strftime("%Y_%m_%d_%H_%M_%S", gmtime())

        with hide('running', 'stdout', 'aborts'):
            try:
                if os.path.isfile(local_dir + mysqldump_fname):
                    database = sudo('mysql -h ' + mysql_ip + ' -u ' + mysql_user + ' -p' + password +
                                    ' -e "show databases;" | grep ' + db_name + ' | grep -vi warning')

                    dbparts = database.split('\n')
                    database = dbparts[0]
                    database = database.strip()

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
