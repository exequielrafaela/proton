from fabric.api import settings, run, sudo
from fabric.colors import red, blue, yellow, green
from fabric.decorators import task


@task
def command(cmd):
    """
Run a command in the host/s
    :param cmd: bash command to be executed
    eg: fab -R dev command:hostname
    """
    with settings(warn_only=False):
        run(cmd)
        print blue(cmd)
        print red(cmd)
        print yellow(cmd)
        print green(cmd)


@task
def sudo_command(cmd):
    """
Run a certain command with sudo priviledges
    :param cmd: bash command to be executed as sudo
    #eg : fab -R dev sudo_command:"apt-get install geany"
    """
    with settings(warn_only=False):
        sudo(cmd)


@task
def disk_usage(tree_dir='/'):
    """
Check a certain folder Disk Usage
    :param tree_dir:
    """
    with settings(warn_only=False):
        import os
        disk = os.statvfs(tree_dir)
        print "preferred file system block size: " + str(disk.f_bsize)
        print "fundamental file system block size: " + str(disk.f_frsize)
        print "total number of blocks in filesystem: " + str(disk.f_blocks)
        print "total number of free blocks: " + str(disk.f_bfree)
        print "free blocks available to non-super user: " + str(disk.f_bavail)
        print "total number of file nodes: " + str(disk.f_files)
        print "total number of free file nodes: " + str(disk.f_ffree)
        print "free nodes available to non-super user: " + str(disk.f_favail)
        print "flags: " + str(disk.f_flag)
        print "miximum file name length: " + str(disk.f_namemax)
        print "~~~~~~~~~~calculation of disk usage:~~~~~~~~~~"
        total_bytes = float(disk.f_frsize * disk.f_blocks)
        print "total space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_bytes, total_bytes / 1024, total_bytes / 1024 / 1024, total_bytes / 1024 / 1024 / 1024)
        total_used_space = float(disk.f_frsize * (disk.f_blocks - disk.f_bfree))
        print "used space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_used_space, total_used_space / 1024, total_used_space / 1024 / 1024,
            total_used_space / 1024 / 1024 / 1024)
        total_avail_space = float(disk.f_frsize * disk.f_bfree)
        print "available space: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes" % (
            total_avail_space, total_avail_space / 1024, total_avail_space / 1024 / 1024,
            total_avail_space / 1024 / 1024 / 1024)
        total_avail_space_non_root = float(disk.f_frsize * disk.f_bavail)
        print "available space for non-super user: %d Bytes = %.2f KBytes = %.2f MBytes = %.2f GBytes " % (
            total_avail_space_non_root, total_avail_space_non_root / 1024, total_avail_space_non_root / 1024 / 1024,
            total_avail_space_non_root / 1024 / 1024 / 1024)
