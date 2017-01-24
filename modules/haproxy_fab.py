from fabric.api import settings, sudo, cd
from fabric.contrib.files import sed
from fabric.decorators import task
from termcolor import colored


@task
def haproxy_ws(action, ws_ip):
    """
Add/Remove a WS from a Haproxy Load Balancer
    :param action: "add" or "remove"
    :param ws_ip: Web Server IP Address
    """
    with settings(warn_only=False):
        with cd('/etc/haproxy'):
            try:
                ws_conf = sudo('sudo cat haproxy.cfg | grep "' + ws_ip + ':80 weight 1 check" | head -n1')
                # ws_conf = str(ws_conf.lstrip())
                print colored('=========================================', 'blue')
                print colored('Server ' + ws_ip + ' FOUND in haproxy.cfg', 'blue')
                print colored('=========================================', 'blue')
                print colored(ws_conf, 'cyan', attrs=['bold'])

                if ws_conf == "":
                    print colored('=========================================', 'red')
                    print colored('Server ' + ws_ip + ' NOT FOUND in haproxy.cfg', 'red')
                    print colored('=========================================', 'red')

                elif "disabled" in ws_conf and action == "add":
                    # we erase the last word "disabled" & create the new file add_ws
                    add_ws = ws_conf.rsplit(' ', 1)[0]
                    print colored('=========================================', 'blue')
                    print colored('SERVER ' + ws_ip + ' WILL BE ADDED to the HLB', 'blue')
                    print colored('=========================================', 'blue')
                    print colored('Line to be ADDED:', attrs=['bold'])
                    print colored(add_ws, 'cyan', attrs=['bold'])

                    print colored('Line to be REMOVED:', attrs=['bold'])
                    remove_ws = ws_conf
                    print colored(remove_ws, 'cyan', attrs=['bold'])

                    sudo('chmod 757 /etc/haproxy/')
                    sudo('chmod 606 /etc/haproxy/haproxy.cfg')
                    sed('/etc/haproxy/haproxy.cfg', remove_ws, add_ws, limit='', use_sudo=True, backup='.bak', flags='',
                        shell=False)
                    # fabric.contrib.files.sed(filename, before, after, limit='', use_sudo=False,
                    #  backup='.bak', flags='', shell=False)
                    # sudo('sed -i "/'+remove_ws+'/c\'+add_ws+' haproxy.cfg')
                    sudo('chmod 755 /etc/haproxy/')
                    sudo('chmod 600 /etc/haproxy/haproxy.cfg')

                    sudo('systemctl restart haproxy')

                    print colored('=============================================', 'blue', attrs=['bold'])
                    print colored('SERVER ' + ws_ip + ' SUCCESFULLY ADDED to HLB', 'blue', attrs=['bold'])
                    print colored('=============================================', 'blue', attrs=['bold'])

                elif "disabled" not in ws_conf and action == "remove":
                    add_ws = ws_conf + " disabled"
                    print colored('=================================================', 'blue')
                    print colored('SERVER ' + ws_ip + ' WILL BE REMOVED from the HLB', 'blue')
                    print colored('=================================================', 'blue')
                    print colored('Line to be ADDED:', attrs=['bold'])
                    print colored(add_ws, 'cyan', attrs=['bold'])

                    print colored('Line to be REMOVED:', attrs=['bold'])
                    remove_ws = ws_conf
                    print colored(remove_ws, 'cyan', attrs=['bold'])

                    sudo('chmod 757 /etc/haproxy/')
                    sudo('chmod 606 /etc/haproxy/haproxy.cfg')
                    sed('/etc/haproxy/haproxy.cfg', remove_ws, add_ws, limit='', use_sudo=True, backup='.bak', flags='',
                        shell=False)
                    sudo('chmod 755 /etc/haproxy/')
                    sudo('chmod 600 /etc/haproxy/haproxy.cfg')

                    sudo('systemctl restart haproxy')

                    print colored('================================================', 'blue', attrs=['bold'])
                    print colored('SERVER ' + ws_ip + ' SUCCESFULLY REMOVED from HLB', 'blue', attrs=['bold'])
                    print colored('================================================', 'blue', attrs=['bold'])

                else:
                    print colored('===========================================================================', 'red')
                    print colored('WRONG ARGs or conditions unmets, eg: trying to add a WS that already exists', 'red')
                    print colored('===========================================================================', 'red')
            except SystemExit:
                print colored('=======================================================', 'red')
                print colored('Problem found haproxy.cfg not found - check istallation', 'red')
                print colored('=======================================================', 'red')
