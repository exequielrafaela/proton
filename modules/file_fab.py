# coding=utf-8
# Import Fabric's API module#
from fabric.api import settings, env, put, get
from fabric.decorators import task


@task
def send(localpath, remotepath):
    """
Send a file to the host/s
    :param localpath: file local path
    :param remotepath: file remote path
    eg: fab -R dev file_send:path/to/edited/ssh_config,/etc/ssh/ssh_config
    # or if the modified ssh_config is in the directory where you’re running Fabric:
    eg: fab file_send:ssh_config,/etc/ssh/ssh_config
    """
    with settings(warn_only=False):
        put(localpath, remotepath, use_sudo=True)


@task
def send_mod(localpath, remotepath, modep):
    """
Send a file to the host/s specifying it's permissions
    :param localpath: file local path
    :param remotepath: file remote path
    :param modep:
    eg: fab -R dev file_send_mod:path/to/edited/ssh_config,/etc/ssh/ssh_config,0755
    """
    with settings(warn_only=False):
        put(localpath, remotepath, mode=modep, use_sudo=True)


@task
def send_oldmod(localpath, remotepath):
    """
Send a file to the host/s mirroring local permissions
    :param localpath: file local path
    :param remotepath: file remote path
    eg: fab -R dev file_send_oldmod:path/to/edited/ssh_config,/etc/ssh/ssh_config
    """
    with settings(warn_only=False):
        put(localpath, remotepath, mirror_local_mode=True, use_sudo=True)


@task
def get(remotepath, localpath):
    """
Retrievng a file from the host/s
    :param remotepath: file remote path
    :param localpath: file local path
    eg: fab -R dev get_file:/var/log/auth.log,/tmp/auth.log
    """
    with settings(warn_only=False):
        get(remotepath, localpath + "." + env.host)
