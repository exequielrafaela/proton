#PROTON
*_Proton is a Python Fabric based CM&D (Configuration Management & Deployment) Custom Tool._*

*In this repo you'll find all the Proton project files. 1st you'll be able to generate an provisioning user and it's shh keys to test them in a list of remote Servers. Afterwards you'll use any of the Proton Standard functions targeting your manually configured ServerList.*

<p align="center">
  <b>Some Related Links:</b><br>
  <a href="#">https://goo.gl/Nda5sd</a> |
  <a href="#">goo.gl/fKiM57</a> |
  <a href="#">https://goo.gl/yMNmON</a> |
  <a href="#">http://docs.fabfile.org/en/1.12/</a>
  <br><br>
  <img src="https://github.com/exequielrafaela/proton/blob/dev-test/Figures/fabric_pyenv.png" 
</p>

Execution example: 
	
**1st Pre requisites:** Run the requirements.sh script that comes with proton
	
	 $ git clone https://github.com/exequielrafaela/proton.git
	 $ cd proton
	 $ sudo ./requirements.sh


**2nd Proton help:** Useful command guide
	
	$ fab show_help 
	./conf/

	Commands list:

	fab show_help                Change behaviour mode to passive
	fab -l                       To list all the fabric functions defined in proton
	fab -d "task_name"           To list all the fabric functions defined in proton
	fab show_roles               Change behaviour mode to aggressive
	
	s, q, quit, exit             Exit

	Done.

 <img src="https://github.com/exequielrafaela/proton/blob/dev-test/Figures/proton-multi-node-deployment-workflow.png" 
 </p>

**3rd Proton Available Commands:** inside the proton folder run "fab -l" 
	
	$ fab -l
	
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

	Available commands:

    	OptionParser                                         Class attributes:
    	apt_package                                          Install/Upgrade an Debian apt based linux package
    	cachefs_install                                      cachefilesd (NFS Cache) installation function
    	change_pass                                          Change RedHat/Centos based OS user password
    	colored                                              Colorize text.
    	command                                              Run a command in the host/s
    	disk_usage                                           Check a certain folder Disk Usage
    	download_data_from_server                            Get data from a remote host passing the local data_dir and the
    	download_feeds_from_server                           Download LAMP data using download_data_from_server task
    	download_lamp_from_server                            Download LAMP data using download_data_from_server task
    	file_get                                             Retrievng a file from the host/s
    	file_send                                            Send a file to the host/s
    	file_send_mod                                        Send a file to the host/s specifying it's permissions
    	file_send_oldmod                                     Send a file to the host/s mirroring local permissions
    	gmtime                                               gmtime([seconds]) -> (tm_year, tm_mon, tm_mday, tm_hour, tm_min,
    	haproxy_ws                                           Add/Remove a WS from a Haproxy Load Balancer
    	install_docker_centos7                               Install Docker Engine, docker-compose, docker-machine
    	install_lamp_centos7                                 LAMP Stack installation in Centos7 OS.
    	install_various_centos7                              Install custom list of packets
    	key_append                                           Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    	key_gen                                              Generate an SSH key for a certain user
    	key_read_file                                        In the localhost read and return as a string the public ssh key file given as parameter
    	key_remove                                           Append the public key string in the /home/usernamea/.ssh/authorized_keys of the host
    	key_test                                             Test SSH (authorized_keys) in the host
    	knifezero_conf_centos                                Initialize knife zero on RedHat/Centos OS
    	knifezero_install_centos                             Install knife zero on RedHat/Centos OS
    	load_configuration                                   Load configurations from file artemisa.conf
    	maltrail                                             Instaling maltrail IDS as Server or Sensor
    	mysql_backup_all                                     MySQLdump backup for all databases
    	mysql_backup_db                                      MySQLdump backup for a certain DB passed as argument
    	mysql_backup_db_from_conf                            MySQLdump backup for a certain DB passed as argument
    	mysql_backup_db_rds                                  MySQLdump backup for a certain DB passed as argument
    	mysql_backup_db_rds_from_conf                        MySQLdump backup for a certain DB passed as argument
    	mysql_backup_db_rds_from_conf_ggcc_prd               MySQLdump backup for a certain DB passed as argument
    	mysql_backup_db_rds_from_conf_ggcc_stg               MySQLdump backup for a certain DB passed as argument
    	mysql_create_db                                      Create a MySQL Database with the given db_name
    	mysql_create_local_user                              Create a localhost MySQL user
    	mysql_grant_remote_cx                                Grant MySQL remote conection from a certain host
    	mysql_grant_user_db                                  Given the username, grant MySQL permissions for a certain DB to this username
    	mysql_grant_user_db_rds_with_conf                    Given the username, grant MySQL permissions for a certain DB to this username
    	mysql_install_client_centos7                         Install the mysql client in a Centos7 based OS
    	mysql_restore_rds_to_new_db_from_conf                MySQLdump restore
    	mysql_restore_rds_to_new_db_from_conf_ggcc_stg       MySQLdump restore
    	mysql_restore_rds_to_new_db_from_conf_ggcc_stg_back  MySQLdump restore
    	mysql_restore_to_new_db                              MySQLdump restore
    	mysql_restore_upgrade_all                            MySQLdump restore and upgrade for all DBs
    	mysql_sh_db_user                                     MySQLdump backup
    	nfs_client_centos6                                   Installing NFS Client for Centos6 system host/s
    	nfs_client_centos7                                   Installing NFS Client for Centos7 system host/s
    	nfs_server_centos6                                   Installing NFS Server on a Centos6 host
    	nfs_server_centos7                                   Installing NFS Server on a Centos7 host
    	nfs_server_ubuntu                                    Install in the host7s NFS Server under Debian/Ubuntu based systems
    	password_base64_decode                               Password base64 decode
    	password_base64_encode                               Password base64 encode
    	password_hash                                        Password hash func
    	password_hash_verify                                 Password hash verify func
    	pbkdf2_sha256                                        This class implements a generic ``PBKDF2-HMAC-SHA256``-based password hash, and follows the :ref:`password-hash-api`.
    	php53_install_centos7                                Install php-5.3.29 in a CentOS7 Server
    	php53_remove_centos7                                 Remove php-5.3.29 in a CentOS7 Server
    	rsync                                                Python fabric rsync
    	rsync_data_from_server                               Migrate the data from a LAMP Server to a new one mainly using rsync
    	rsync_data_to_server                                 Migrate the data from a Jumphost Server to a new LAMP Server mainly using rsync
    	rsync_data_to_server_v2                              Migrate the data from a Jumphost Server to a new Server mainly using rsync
    	ruby_install_centos                                  Install ruby via rvm in Centos based system
    	show_help                                            Show proton help
    	show_roles                                           Show the fabric declared roles
    	strftime                                             strftime(format[, tuple]) -> string
    	strtobool                                            Convert a string representation of truth to true (1) or false (0).
    	sudo_command                                         Run a certain command with sudo priviledges
    	sudoers_group                                        Modify /etc/sudoers adding sudo NOPASSWD wheel group (Still Incomplete)
    	upload_lamp_from_server                              Upload LAMP stack data using rsync_data_to_server_v2 task
    	user_add_centos                                      Add a user in RedHat/Centos based OS
    	user_add_ubuntu                                      Add a user in Debian/Ubuntu based OS
    	yum_package                                          Install/Upgrade an RedHat/Centos yum based linux package


**4th Check the arguments of each Proton Function:** Before running a Proton command you should check the expected parameters you must pass to it.
	
	$ fab -d mysql_backup_all
	Displaying detailed information for task 'mysql_backup_all':

    	MySQLdump backup for all databases
    	fab -R devtest mysql_backup:/tmp/,/tmp/,root,127.0.0.1
    	NOTE: Consider that the role after -R hast to be the remote MySQL Server.
        	:param local_dir: mysqldump jumphost/bastion destination directory
        	:param remote_dir: mysqldump remote host destination directory
        	:param mysql_user: MySQL Server Admin User
        	:param mysql_ip: MySQL Server IP Address
    
    	Arguments: local_dir, remote_dir, mysql_user, mysql_ip='127.0.0.1'
	

**5th Validate the manually configured Proton Roles:** Use the standar Proton "show_roles" function to check your roles
	
	$ fab show_roles
	./conf/
	devtest ['10.191.231.182', '10.191.231.203']
	local ['localhost']

	Done.




