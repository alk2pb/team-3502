#!/usr/bin/env python
##
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = 'Rodrigo Augosto (@coto)'
__website__ = 'www.beecoss.com'

import os
import sys
# Third party libraries path must be fixed before importing webapp2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bp_includes/external'))

import webapp2

# Arduino to Database
from google.appengine.ext import ndb
import datetime
from lib import utils
from google.appengine.api import users


class ArduinoSensorData(ndb.Model):
    #test = ndb.StringProperty(default="")
    #test1 = ndb.StringProperty(default="")
    #test2 = ndb.StringProperty(default="")
    email = ndb.StringProperty()
    weight = ndb.IntegerProperty(default=0)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    
class ArduinoPost(webapp2.RequestHandler):
    def post(self):
        sensordata = ArduinoSensorData()
        try:
            #get values
            weight = int(self.request.get('weight'))
            email_or_username = str(self.request.get('email')).lower().strip()
            #password = str(self.request.get('password'))
            #sensordata.test = "yes"
            
            #check if we got an email or username
            if utils.is_email_valid(email_or_username):
                #sensordata.test1 = "yes"
                #user_info = users.get_by_email(email_or_username)
                user = users.User(email_or_username)
                #password = utils.hashing(password, self.app.config.get('salt'))
                
                #auth_id = user_info.auth_ids[0]
                
                # authenticate user by its password
                #try:
                #    self.user_model.get_by_auth_password(auth_id, password)
                #    sensordata.test2 = "yes"
                    
                
                #except (InvalidAuthIdError, InvalidPasswordError):
                #    sensordata.test2 = "no"
                #    pass
                if user:
                    sensordata.email = email_or_username
                    sensordata.weight = weight
                    sensordata.timestamp = datetime.datetime.now()
                    sensordata.put()
            
                
        except ValueError:
            #sensordata.test = "no"
            pass

import csv

class Export(webapp2.RequestHandler):
  def get(self):
      user = users.get_current_user()
          
      data = ArduinoSensorData.query(ArduinoSensorData.email == user.email).order(ArduinoSensorData.timestamp)
      self.response.headers['Content-Type'] = 'application/csv'
      self.response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
      writer = csv.writer(self.response.out)
      writer.writerow(["timestamp", "weight"])
      for row in data:
          writer.writerow([str(row.timestamp), str(row.weight)])
      

from bp_includes.lib.error_handler import handle_error
from bp_includes import config as config_boilerplate

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bp_content/themes/', os.environ['theme']))
# Import Config Importing
import config as config_theme

# Routes Importing
from bp_admin import routes as routes_admin
from bp_includes import routes as routes_boilerplate
import routes as routes_theme


webapp2_config = config_boilerplate.config
webapp2_config.update(config_theme.config)

app = webapp2.WSGIApplication([('/arduino_post', ArduinoPost),('/export', Export)], debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'), config=webapp2_config)

if not app.debug:
    for status_int in app.config['error_templates']:
        app.error_handlers[status_int] = handle_error

routes_theme.add_routes(app)
routes_boilerplate.add_routes(app)
routes_admin.add_routes(app)
