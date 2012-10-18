#!/usr/bin/env python
#
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

import jinja2
import os
import logging
import random
import string

from google.appengine.api import mail
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


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
    # 1 contact, 2 forward, 3 expired email
    messge_type = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))

class AboutPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/about.html')
        self.response.out.write(template.render(template_values))
        
class AboutExamplePage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/about_example.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/about_example.html')
        self.response.out.write(template.render(template_values))       

class ContactPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/contact.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        errors = []
        
        post_sender = self.request.get('contact_request[sender_name]')
        post_email = self.request.get('contact_request[email]')
        post_details = self.request.get('contact_request[details]')
        
        if len(post_sender) == 0:
            errors.append('Sender name can\'t be blank')
        
        if len(post_email) == 0:
             errors.append('Email can\'t be blank')
        elif not mail.is_email_valid(post_email):
             errors.append('Email must be a valid email')
        
        if len(post_details) == 0:
             errors.append('Details can\'t be blank')
        
        error = False
        notice = False
        if len(errors) > 0:
            error = '<div class="formErrors contactrequestErrors alert-message"><h5>Could not submit your contact request</h5><ul>'
            for e in errors:
                error += '<li>'+e+'</li>'
            error += '</ul></div>'
        else:
            
            mail.send_mail(sender=post_sender,
                          to="support@inkscribbles.com",
                          subject="Messge.me Contact Request",
                          body=post_details)
            
            notice = 'Your message was successfully sent.'
            post_sender = ''
            post_email = ''
            post_details = ''
        
        template_values = {
            'error': error,
            'notice': notice,
            'post_sender': post_sender,
            'post_email': post_email,
            'post_details': post_details
        }
        
        template = jinja_environment.get_template('templates/contact.html')
        self.response.out.write(template.render(template_values))

class MessgesPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        template_values = {}
        
        template = jinja_environment.get_template('templates/messges_new.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        
        errors = []
        
        post_owner = self.request.get('messager[owner]')
        post_message = self.request.get('messager[message]')
        
        if len(post_owner) == 0:
            errors.append('Your email address can\'t be blank')
        elif not mail.is_email_valid(post_owner):
             errors.append('Email must be a valid email')
        
        # # Check for existing email signup
        # existing = db.GqlQuery("SELECT * "
        #                     "FROM Messagers "
        #                     "WHERE owner = :1 "
        #                     "ORDER BY date DESC LIMIT 1",
        #                     post_owner)
        # 
        # if len(existing) > 0:
        #     errors.append('')
        
        error = False
        notice = False
        if len(errors) > 0:
            error = '<div class="formErrors contactrequestErrors alert-message"><h5>Error creating your messger! Almost there</h5><ul>'
            for e in errors:
                error += '<li>'+e+'</li>'
            error += '</ul></div>'
        else:
            
            logging.info('No Errors, creating messager')
            
            messager = Messager()
            messager.owner = post_owner
            messager.message = post_message
            messager.enabled = True
            
            # Create owner token
            hash = ''.join(random.choice(string.lowercase + string.digits) for i in xrange(10))
            
            # Check for existing hash
            existing = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE token = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                hash).get()
            while existing is not None:
                # Create owner token
                hash = ''.join(random.choice(string.lowercase + string.digits) for i in xrange(10))
                
                # Check for existing hash
                existing = db.GqlQuery("SELECT * "
                                    "FROM Messager "
                                    "WHERE token = :1 "
                                    "ORDER BY date DESC LIMIT 1",
                                    hash).get()
            
            
            # Store the token
            messager.token = hash
            logging.info('Created token '+messager.token)
            
            # Create the messgekey
            hash = ''.join(random.choice(string.lowercase) for i in xrange(4))
            
            # Check for existing hash
            existing = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE messgekey = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                hash).get()
            while existing is not None:
                # Create owner token
                hash = ''.join(random.choice(string.lowercase) for i in xrange(4))
                
                # Check for existing hash
                existing = db.GqlQuery("SELECT * "
                                    "FROM Messager "
                                    "WHERE messgekey = :1 "
                                    "ORDER BY date DESC LIMIT 1",
                                    hash).get()
            
            # Store the messagekey
            messager.messgekey = hash
            
            logging.info('Created messgekey '+messager.messgekey)
            
            # Save the messager to datastore
            messager.put()
            
            message = mail.EmailMessage(sender="Messge.me Mailbot <mailer@messge.me>",
                                        subject="New messge.me account created")
            message.to = messager.owner
            message.body = """
Welcome to messge.me

You have received this email because your email was used to register an account at messge.me

While your account is active, any emails sent to {0}@messge.me or any messages entered at
http://messge.me/m/{1} will be forwarded to this address.

This means you can give out the messge.me email or web address to receive emails and messages to your personal email account without ever giving out your real details!

To edit or cancel you account you can http://messge.me/messges/{2}/edit

We hope you find this service useful.

If you did not sign up for the service, please access the link above and disable your account.

Regards

messge.me messagebot
            """.format(messager.messgekey, messager.messgekey, messager.token)
            
            message.html = """
<h2>Welcome to messge.me</h2>

<p>You have received this email because your email was used to register an account at <a href="http://messge.me">messge.me</a></p>

<p>
  While your account is active, any emails sent to {0}@messge.me or any messages entered at
    <a href="http://messge.me/m/{1}">http://messge.me/m/{2}</a> will be forwarded to this address.
</p>

<p>
  This means you can give out the messge.me email or web address to receive emails and messages to your personal email account without ever giving out your real details!
</p>

<p>
  To edit or cancel you account you can manage your account at <a href="http://messge.me/messges/{3}/edit">http://messge.me/messges/{4}/edit</a>
</p>

<p>
  We hope you find this service useful.
</p>

<p>
  If you did not sign up for the service, please access the link above and disable your account.
</p>

<p>Regards</p>
<p>messge.me messagebot</p>
            """.format(messager.messgekey, messager.messgekey, messager.messgekey, messager.token, messager.token)
            
            message.send()
            
            self.redirect('/messges/'+messager.token+'/edit?signup=true')
        
        template_values = {
            'error': error,
            'notice': notice,
            'post_owner': post_owner,
            'post_message': post_message
        }
        
        template = jinja_environment.get_template('templates/messges_new.html')
        self.response.out.write(template.render(template_values))       
        
class MessgesEditPage(webapp2.RequestHandler):
    def get(self, token):
        self.response.headers['Content-Type'] = 'text/html'
        
        logging.info("Got token "+token)
        
        messager = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE token = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                token).get()
        
        if messager == None:
            webapp2.abort(404)
        
        template_values = {
            'messager': messager,
            'signup': self.request.get('signup')
        }
        
        template = jinja_environment.get_template('templates/messges_edit.html')
        self.response.out.write(template.render(template_values))
    def post(self, token):
        self.response.headers['Content-Type'] = 'text/html'
        
        logging.info("Got token "+token)
        
        messager = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE token = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                token).get()
        
        if messager == None:
            webapp2.abort(404)
        
        post_message = self.request.get('messager[message]')
        post_enabled = self.request.get('messager[enabled]')
        
        messager.message = post_message
        logging.info("Got enabled "+post_enabled)
        if post_enabled == '1':
            messager.enabled = True
        else:
            messager.enabled = False
        
        messager.put()
        
        template_values = {
            'messager': messager,
            'updated': True
        }
        
        template = jinja_environment.get_template('templates/messges_edit.html')
        self.response.out.write(template.render(template_values))

class MessgesSendPage(webapp2.RequestHandler):
    def get(self, key):
        self.response.headers['Content-Type'] = 'text/html'
        
        logging.info("Got key "+key)
        
        messager = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE messgekey = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                key).get()
        
        if messager == None:
            webapp2.abort(404)
        
        template_values = {
            'messager': messager
        }
        
        if messager.enabled:
            template = jinja_environment.get_template('templates/messges_send.html')
        else:
            template = jinja_environment.get_template('templates/messges_expired.html')
        
        self.response.out.write(template.render(template_values))
    def post(self, key):
        self.response.headers['Content-Type'] = 'text/html'
        
        logging.info("Got key "+key)
        
        messager = db.GqlQuery("SELECT * "
                                "FROM Messager "
                                "WHERE messgekey = :1 "
                                "ORDER BY date DESC LIMIT 1",
                                key).get()
        
        if messager == None:
            webapp2.abort(404)
        
        errors = []
        
        post_email = self.request.get('contact_form_request[email]')
        post_subject = self.request.get('contact_form_request[subject]')
        post_details = self.request.get('contact_form_request[details]')
        
        if len(post_email) == 0:
            errors.append('Your email address can\'t be blank')
        elif not mail.is_email_valid(post_email):
             errors.append('Email must be a valid email')
        
        if len(post_subject) == 0:
            errors.append('Your subject can\'t be blank')
        
        if len(post_details) == 0:
            errors.append('Your details can\'t be blank')
        
        error = False
        notice = False
        if len(errors) > 0:
            error = '<div class="formErrors contactrequestErrors alert-message"><h5>Error sending your message. Almost there</h5><ul>'
            for e in errors:
                error += '<li>'+e+'</li>'
            error += '</ul></div>'
        else:
            if messager.enabled:
                
                sent = Sent()
                sent.messge_type = 1
                sent.messager_id = messager.key()
                sent.put()
                
                # send the email
                mail.send_mail(sender='mailer@messge.me',
                          to=messager.owner,
                          subject=post_subject+" - courtesy of messge.me",
                          body=post_details+"""
                          
                          
--------------------------------------
You got this email from your messge.me account. If you do not wish to receive any further emails please disable your account.
Edit your account at http://messge.me/messges/{0}/edit                          
                          """.format(messager.token)
                          )
            
                notice = 'Your message was successfully sent.'
                
            
        template_values = {
            'messager': messager,
            'error': error,
            'notice': notice,
            'post_email': post_email,
            'post_subject': post_subject,
            'post_details': post_details
        }
        
        if messager.enabled:
            template = jinja_environment.get_template('templates/messges_send.html')
        else:
            template = jinja_environment.get_template('templates/messges_expired.html')
        
        self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([
                                ('/', MainPage),
                                ('/about', AboutPage),
                                ('/about/example', AboutExamplePage),
                                ('/contact/new', ContactPage),
                                ('/messges/new', MessgesPage),
                                webapp2.Route(r'/messges/<token:[^/]+>/edit', MessgesEditPage),
                                webapp2.Route(r'/m/<key:[^/]+>', MessgesSendPage)
                              ],
                              debug=True)
