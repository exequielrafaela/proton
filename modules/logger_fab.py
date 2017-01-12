# -*- coding: UTF-8 -*-

# This is part of Artemisa.
# 
# Artemisa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Artemisa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Artemisa.  If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.handlers
import os
from time import strftime

LOG_PATH = './logs'

def CreateLogger(logger, log_file):
    info = logger.info
    debug = logger.debug
    warning = logger.warning
    critical = logger.critical
    error = logger.error
    exception = logger.exception

    File_created = True

    # Create the directory
    if not os.path.exists(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)
        except OSError:
            File_created = False

    file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")
    cons_formatter = logging.Formatter("%(asctime)s %(message)s")

    try:
        file_hdl = logging.FileHandler(log_file)
        file_hdl.setFormatter(file_formatter)
    except IOError:
        File_created = False

    cons_hdl = logging.StreamHandler()
    cons_hdl.setLevel(logging.INFO) 
    cons_hdl.setFormatter(cons_formatter)

    if File_created:
        logger.addHandler(file_hdl)
                
    logger.addHandler(cons_hdl)
    logger.setLevel(logging.DEBUG)

    if not File_created:
        logger.warning("Cannot create the log file. Logging to " + log_file +" is disabled.")


logger_log_file = LOG_PATH + "/" + "artemisa" + "_" + strftime("%Y-%m-%d") + ".log"
pjsua_logger_log_file = LOG_PATH + "/" + "artemisa_pjsua" + "_" + strftime("%Y-%m-%d") + ".log"

logger = logging.getLogger(logger_log_file)
pjsua_logger = logging.getLogger(pjsua_logger_log_file)

CreateLogger(logger, logger_log_file)
CreateLogger(pjsua_logger, pjsua_logger_log_file)
