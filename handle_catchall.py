#  Messgeme
#
#  Created by Timothy Marks on 5/1/12.
#  Copyright (c) 2012 Ink Scribbles Pty Ltd.
#
#  This file is part of Messgeme.
# 
#  Messgeme is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  Messgeme is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with Messgeme.  If not, see <http://www.gnu.org/licenses/>.

import logging, email

import wsgiref.handlers

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import db
from google.appengine.api import mail

### Models
class Messager(db.Model):
    owner = db.StringProperty(multiline=False)
    token = db.StringProperty(multiline=False)
    messgekey = db.StringProperty(multiline=False)
    
    message = db.StringProperty(multiline=True)
    
    theme = db.IntegerProperty()
    enabled = db.BooleanProperty()
    
    date = db.DateTimeProperty(auto_now_add=True)

class Sent(db.Model):
    messager_id = db.ReferenceProperty(Messager)
    messge_type = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MessgeSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        
        to = mail_message.to
        try:
            cc = mail_message.cc
        except:
            cc = None
        
        to_emails = []
        
        if to is not None:
            for address in to.split(","):
                index = address.find("@messge.me")
                if index != -1:
                    # found a @messge.me address
                    if (index - 4) >=0:
                        to_emails.append(address[(index-4):4])
                        continue
                # index = address.find("@messgeme.appspotmail.com")
                # if index != -1:
                #     # found a @messge.me address
                #     if (index - 4) >=0:
                #         to_emails.append(address[(index-4):4])
                #         continue               
         
        if cc is not None:
            for address in cc.split(","):
                index = address.find("@messge.me")
                if index != -1:
                    # found a @messge.me address
                    if (index - 4) >=0:
                        to_emails.append(address[(index-4):4])
                        continue
                # index = address.find("@messgeme.appspotmail.com")
                # if index != -1:
                #     # found a @messge.me address
                #     if (index - 4) >=0:
                #         to_emails.append(address[(index-4):4])
                #         continue
        
        if len(to_emails) == 0:
            logging.info("Got an email to no members")
            logging.info("To: "+mail_message.to)
            logging.info("Sender: "+mail_message.sender)
            
            plaintext_bodies = mail_message.bodies('text/plain')
            html_bodies = mail_message.bodies('text/html')
                
            for content_type, body in plaintext_bodies:
                logging.info("Got plaintext body "+body.decode())
                break
                
            for content_type, body in html_bodies:
                logging.info("Got html body "+body.decode())
                break
                
            return
        
        for mm in to_emails:
            
            logging.info("Found messge key "+mm)
            messager = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE messgekey = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                mm).get()
            
            if messager == None:
                continue
            
            if messager.enabled:
                
                # Forward email
                
                sent = Sent()
                sent.messge_type = 2
                sent.messager_id = messager.key()
                sent.put()
                
                message = mail.EmailMessage(sender="Messge.me Mailbot <mailer@messge.me>",
                                            to=messager.owner,
                                            reply_to=mail_message.sender,
                                            subject=mail_message.subject+" - via messge.me")
    
                
                plaintext_bodies = mail_message.bodies('text/plain')
                html_bodies = mail_message.bodies('text/html')
                
                for content_type, body in plaintext_bodies:
                    #logging.info("Got plaintext body "+body.decode())
                    decoded_body = body.decode()
                    message.body = decoded_body+"""
                          
                          
--------------------------------------
You got this email from your messge.me account. If you do not wish to receive any further emails please disable your account.
Edit your account at http://messge.me/messges/{0}/edit                          
                          """.format(messager.token)
                    break
                
                for content_type, body in html_bodies:
                    #logging.info("Got html body "+body.decode())
                    decoded_html = body.decode()
                    message.html = decoded_html+"""
                                               
<hr />
<p>
    You got this email from your messge.me account. If you do not wish to receive any further emails please disable your account.
</p>

<p>
    Edit your account at <a href="http://messge.me/messges/{0}/edit">http://messge.me/messges/{1}/edit</a>
</p>                         
                          """.format(messager.token, messager.token)
                    break
                    
                message.send()
                
            else:
                
                sent = Sent()
                sent.messge_type = 3
                sent.messager_id = messager.key()
                sent.put()
                
                # Send email expired message
                message = mail.EmailMessage(sender="Messge.me Mailbot <mailer@messge.me>",
                                        subject="Address Expired - "+messager.messgekey)
                message.to = messager.owner
                message.body = """
You got this email because the email address you attempted to send to has expired. This is probably because the messge.me account was closed or the contact information was invalid.

--------------------------------------
messge.me provides private email contact forms and email forwarders. The address you were provided was a private email forwarder that no longer exists, therefore there is no longer a way to contact this person.

Please see http://messge.me for more details
                """
            
                message.html = """
<p>
  You got this email because the email address you attempted to send to has expired. This is probably because the messge.me account was closed or the contact information was invalid.
</p>

<hr />
<p>
  messge.me provides private email contact forms and email forwarders. The address you were provided was a private email forwarder that no longer exists, therefore there is no longer a way to contact this person.
</p>
<p>
  Please see <a href="http://messge.me">http://messge.me</a> for more details.
</p>
                """
            
                message.send()
            
        
def main():
    application = webapp.WSGIApplication([MessgeSenderHandler.mapping()], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()