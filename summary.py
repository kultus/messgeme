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

import webapp2

import logging
import datetime

from google.appengine.api import mail
from google.appengine.ext import db

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
    
class Summary(webapp2.RequestHandler):
    def get(self):
        
        lastWeek = datetime.date.today() - datetime.timedelta(weeks=1)
        
        logging.info("Summary since "+str(lastWeek))
        
        signups = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE date >= :1 "
                                "ORDER BY date DESC", lastWeek).count()
        
        logging.info("Got signups "+str(signups))
        
        sent_page_count = db.GqlQuery("SELECT * "
                              "FROM Sent "
                              "WHERE date >= :1 AND messge_type = 1" 
                              "ORDER BY date DESC", lastWeek).count()
        
        logging.info("Got Sent From Pages "+str(sent_page_count))
                              
        sent_email_count = db.GqlQuery("SELECT * "
                            "FROM Sent "
                            "WHERE date >= :1 AND messge_type = 2 "
                            "ORDER BY date DESC", lastWeek).count()
        
        logging.info("Got Sent From Email "+str(sent_email_count))
                            
        sent_expired_count = db.GqlQuery("SELECT * "
                            "FROM Sent "
                            "WHERE date >= :1 AND messge_type = 3 "
                            "ORDER BY date DESC", lastWeek).count()
        
        logging.info("Got Expired "+str(sent_expired_count))
        
        report_summary = """
Messge.me Weekly Summary
========================

Signups                {0}
Page Sent Emails       {1}
Emails Forwarded       {2}
Expired Emails         {3}
        """.format(signups, sent_page_count, sent_email_count, sent_expired_count)
       
        mail.send_mail(sender="mailer@messge.me",
                       to="reports@inkscribbles.com",
                       subject="Messge.me Weekly Summary",
                       body=report_summary)
        
        logging.info("Sent Mail")

    
app = webapp2.WSGIApplication([
  ('/tasks/summary', Summary)
],
debug=True)