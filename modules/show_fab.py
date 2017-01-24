# Import Fabric's API module#
from fabric.api import settings, env
from fabric.decorators import task
from fabric.tasks import Task


@task
def help_proton():
    """
Show proton help
    cmd: fab show_help
    """
    with settings(warn_only=True):
        print ""
        print "Commands list:"
        print ""
        print "fab show_help                        Change behaviour mode to passive"
        print "fab -l                               To list all the fabric functions defined in proton"
        print "fab - -list - format = nested - l    To list all the fabric functions defined in proton"

        print "fab -d \"task_name\"                 To list all the fabric functions defined in proton"
        print "fab show_roles                       Change behaviour mode to aggressive"
        print ""


class ServerRoles(Task):
    name = 'server_roles'

    def run(self):
        """
     Show the fabric declared roles
         cmd: fab show_roles
        """
        pass

    for key, value in sorted(env.roledefs.items()):
        print key, value


sr_instance = ServerRoles()


# def show_roles():
#   """
# Show the fabric declared roles
#    cmd: fab show_roles
#    """
#    for key, value in sorted(env.roledefs.items()):
#        print key, value
