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

# Definition of directories and files
CONFIG_DIR = "./conf/"
RESOURCES_DIR = "./res/"

CONFIG_FILE_PATH = CONFIG_DIR + "artemisa.conf"
ARTEMISA_WEBLOGO_PATH = RESOURCES_DIR + "weblogo.gif"

import ConfigParser                 # Read configuration files.
from smtplib import *
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from modules.logger import logger

class Email():
    """
    This class is used to handle the email part.
    """
    
    def __init__(self):
    
        config = ConfigParser.ConfigParser()
        try:
            strTemp = config.read(CONFIG_FILE_PATH)
        except:
            logger.error("The configuration file artemisa.conf cannot be read.")
            return
        
        if strTemp == []:
            logger.error("The configuration file artemisa.conf cannot be read.")
            return
        else:
            try:

                if config.get("email", "enabled").lower() == "true":
                    self.Enabled = True
                else:
                    self.Enabled = False

                self.SMTP_IP = config.get("email", "smtp_server_ip")
                self.SMTP_PORT = config.get("email", "smtp_server_port")
                self.SMTP_USERNAME = config.get("email", "smtp_server_username")
                self.SMTP_PASSWORD = config.get("email", "smtp_server_password")
                self.From = config.get("email", "from_mail")
                self.Recipients = config.get("email", "recipients_mail")
                self.To_header = config.get("email", "to_header")
                self.Subject = config.get("email", "subject")
                
                if config.get("email", "smtp_server_use_tsl_ssl").lower() == "true":
                    self.TSLSSL = True
                else:
                    self.TSLSSL = False
     
            except:
                logger.error("E-mail account configuration cannot be correctly read. E-mail reports will not be sent.")
                return
    
        del config

    def sendemail(self, strData):
        
        if not self.Enabled: 
            logger.info("E-mail notification is disabled.")
            return
        if self.SMTP_IP == "":
            logger.info("No SMTP server address configured.")
            return
        if self.SMTP_PORT == "":
            logger.info("SMTP server port is not configured.")
            return
        if self.Recipients == "":
            logger.info("No recipient address is configured.")
            return
        
        msg = MIMEMultipart()
        msg['To'] = self.To_header
        msg['From'] = self.From
        msg['Subject'] = self.Subject
        
        msgText = MIMEText(strData, "html")
        msg.attach(msgText)
        
        # Read the logo
        try:
            fp = open(ARTEMISA_WEBLOGO_PATH, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
        except:
            logger.error("Cannot read file " + ARTEMISA_WEBLOGO_PATH)
            return
            
        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<weblogo>')
        msg.attach(msgImage)
        
        try:
            if self.TSLSSL:
                server = SMTP(self.SMTP_IP, int(self.SMTP_PORT))
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            else:
                server = SMTP(self.SMTP_IP, int(self.SMTP_PORT))
                server.ehlo()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
            
            server.sendmail(self.From, self.Recipients.split(","), msg.as_string())
            server.quit()
      
            logger.info("E-mail notification sent.")
        
        except SMTPAuthenticationError:
            logger.warning("E-mail account username and/or password refused by SMTP server.")
        except Exception, e:
            logger.error("E-mail notification couldn't be sent. Error: " + str(e))
        
