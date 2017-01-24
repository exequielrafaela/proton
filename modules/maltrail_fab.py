from fabric.api import settings, sudo, cd, env, run
from fabric.contrib.files import exists
from fabric.decorators import task
from termcolor import colored


@task
def maltrail(role):
    """
Instaling maltrail IDS as Server or Sensor
    :param role: "server" or "sernsor"
    """
    with settings(warn_only=False):
        try:
            # DEPENDENCIAS for AMAZON LINUX:
            # sudo yum install libpcap-devel
            # sudo yum install libnet
            # sudo yum install python-devel
            # sudo yum install gcc-c++
            # sudo yum install git wget
            # wget http://packages.psychotic.ninja/6/base/x86_64/RPMS/schedtool-1.3.0-12.el6.psychotic.x86_64.rpm
            # sudo rpm -Uvh schedtool-1.3.0-12.el6.psychotic.x86_64.rpm
            # wget http://www.coresecurity.com/system/files/pcapy-0.10.6.zip
            # unzip pcapy-0.10.6.zip
            # sudo python setup.py install
            sudo('yum install -y git pcapy schedtool')
            with cd('/home/' + env.user + '/'):
                if exists('/home/' + env.user + '/maltrail', use_sudo=True):
                    print colored('###########################################', 'blue')
                    print colored('####### Directory already created #########', 'blue')
                    print colored('###########################################', 'blue')

                    if role == "sensor":
                        with cd('maltrail'):
                            sudo('python sensor.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    elif role == "server":
                        with cd('/home/' + env.user + '/'):
                            run('[[ -d maltrail ]] || git clone https://github.com/stamparm/maltrail.git')

                        with cd('maltrail/'):
                            sudo('python server.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    else:
                        print colored('=========================================', 'red')
                        print colored('Wrong arg: excects = "sensor" or "server"', 'red')
                        print colored('=========================================', 'red')
                else:
                    print colored('##########################################', 'red')
                    print colored('###### Creating Maltrail Directory #######', 'red')
                    print colored('##########################################', 'red')
                    if role == "sensor":
                        run('git clone https://github.com/stamparm/maltrail.git')
                        with cd('maltrail/'):
                            sudo('python sensor.py ')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')
                            # FOR THE CLIENT #
                            # using configuration file '/home/ebarrirero/maltrail/maltrail.conf.sensor_ok'
                            # using '/var/log/maltrail' for log storage
                            # at least 384MB of free memory required
                            # updating trails (this might take a while)...
                            # loading trails...
                            # 1,135,525 trails loaded

                            # NOTE: #
                            # in case of any problems with packet capture on virtual interface 'any',
                            # please put all monitoring interfaces to promiscuous mode manually
                            #  (e.g. 'sudo ifconfig eth0 promisc')
                            # opening interface 'any'
                            # setting capture filter 'udp or icmp or (tcp and (tcp[tcpflags] == tcp-syn or port 80
                            #  or port 1080 or
                            # port 3128 or port 8000 or port 8080 or port 8118))'
                            # preparing capture buffer...
                            # creating 1 more processes (out of total 2)
                            # please install 'schedtool' for better CPU scheduling
                    elif role == "server":
                        with cd('/home/' + env.user + '/'):
                            run('[[ -d maltrail ]] || git clone https://github.com/stamparm/maltrail.git')
                        with cd('maltrail/'):
                            sudo('python server.py')
                            sudo('ping -c 1 136.161.101.53')
                            sudo('cat /var/log/maltrail/$(date +"%Y-%m-%d").log')

                    else:
                        print colored('=========================================', 'red')
                        print colored('Wrong arg: excects = "sensor" or "server"', 'red')
                        print colored('=========================================', 'red')

                        # To stop Sensor and Server instances (if running in background) execute the following:
                        # sudo pkill -f sensor.py
                        # pkill -f server.py

                        # http://127.0.0.1:8338 (default credentials: admin:changeme!)

                        # If option LOG_SERVER is set, then all events are being sent remotely to the Server,
                        # otherwise they are stored directly into the logging directory set with option LOG_DIR,
                        # which can be found inside the maltrail.conf.sensor_ok file's section [All].

                        # In case that the option UPDATE_SERVER is set, then all the trails are being pulled from
                        # the given location, otherwise they are being updated from trails definitions located inside
                        # the installation itself.

                        # Option UDP_ADDRESS contains the server's log collecting listening address
                        # (Note: use 0.0.0.0 to listen on all interfaces), while option UDP_PORT contains
                        # listening port value. If turned on, when used in combination with option LOG_SERVER,
                        # it can be used for distinct (multiple) Sensor <-> Server architecture.

                        # Same as for Sensor, when running the Server (e.g. python server.py) for the first time
                        # and/or after a longer period of non-running, if option
                        #  USE_SERVER_UPDATE_TRAILS is set to true,
                        # it will automatically update the trails from trail definitions (Note: stored inside the
                        # trails directory).
                        # Should server do the trail updates too (to support UPDATE_SERVER)

        except SystemExit:
            print colored('===========================', 'red')
            print colored('Problem installing MALTRAIL', 'red')
            print colored('===========================', 'red')
