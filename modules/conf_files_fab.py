# Import Fabric's API module#
import ConfigParser
import logging

import sys
from fabric.api import settings
from fabric.decorators import task


@task
def load_configuration(conf_file, section, option):
    """
    Load configurations from file artemisa.conf
    """
    global temp_parser
    # temp_parser = ""
    with settings(warn_only=False):
        config_parser = ConfigParser.ConfigParser()
        try:
            temp_parser = config_parser.read(conf_file)
            # print temp_parser
        except SystemExit:
            logging.critical("The configuration file mysql.conf cannot be read.")
            # if temp_parser == []:
            logging.critical("The configuration file mysql.conf cannot be read.")
            sys.exit(1)
        else:
            try:
                if len(config_parser.sections()) == 0:
                    logging.critical("At least one extension must be defined in extensions.conf.")
                    sys.exit(1)

                # Gets the parameters of mysql
                # self.mysql_section = temp.GetConfigSection(config.CONFIG_SQL_DIR, "mysql")
                # for options in option_list:
                option_value = config_parser.get(section, option)
                # print "Section: " + section + " => " + option + " :" + option_value
                return str(option_value)

            except Exception, e:
                logging.critical(
                    "The configuration file extensions.conf cannot be correctly read. Check it out carefully. "
                    "More info: " + str(e))
                sys.exit(1)
