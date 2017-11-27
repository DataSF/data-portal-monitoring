
# coding: utf-8
#!/usr/bin/env python

import smtplib
#from email.MIMEMultipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.mime.MIMEText import MIMEText
#from email.MIMEBase import MIMEBase
from email.mime.base import *
from email.mime.text import *
from email import encoders
import csv
import time
import datetime
import logging
from retry import retry
import yaml
import os
import itertools
import base64
import inflection
import csv, codecs
#cStringIO
from io import StringIO
from ConfigUtils import *



class Emailer():
    '''
    util class to email stuff to people.
    '''
    def __init__(self, configItems):
        self._config_dir =  configItems['config_dir']
        self._email_config_file = configItems['email_config_file']
        self._emailConfigs = ConfigUtils.setConfigs(self._config_dir, self._email_config_file)
        self._server = None
        self._server_port = None
        self._sender = None
        self._password = None
        self._bcc = None
        self.setConfigs()
        self._recipients = self.getRecipients(self._emailConfigs)

    @staticmethod
    def getRecipients(emailConfigs):
        if 'recipients'in emailConfigs.keys():
            return emailConfigs['recipients']
        return None


    def setConfigs(self):
        self._server = self._emailConfigs['server_addr']
        self._server_port = self._emailConfigs['server_port']
        self._sender =  self._emailConfigs['sender_addr']
        self._bcc = self._emailConfigs['bcc']
        if (self._emailConfigs['sender_password']):
            self._password = base64.b64decode(self._emailConfigs['sender_password'])


    def sendEmails(self,  subject_line, msg_body, fname_attachment=None, fname_attachment_fullpath=None, recipients=None):
        fromaddr = str(self._sender)
        print (fromaddr)
        if(not(recipients)):
            recipients = self._recipients
        toaddr =  recipients
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = recipients
        msg['Subject'] = subject_line
        msg['Bcc'] = self._bcc
        #body = msg_body.decode('utf-8')
        try: 
            body = msg_body.encode().decode()
        except Exception as e:
            print msg_body
            body = msg_body
        msg.attach(MIMEText(body, 'html'))

        #Optional Email Attachment:
        if(not(fname_attachment is None and fname_attachment_fullpath is None)):
            filename = fname_attachment
            attachment = open(fname_attachment_fullpath, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(part)

        #normal emails, no attachment
        server = smtplib.SMTP(self._server, self._server_port)
        ##comment these lines out when using the sfgov email server
        server.starttls()
        password = self._password.decode('utf-8')
        server.login(fromaddr, password)
        ######
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr.split(','), text)
        server.quit()



if __name__ == "__main__":
    main()
