# Copyright 2018 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This class talks directly to the RBM API
endpoint to send and receive messages."""

import json
import os
import re
import uuid
import emoji

from httplib2 import Http
from flask import Flask

from rcs_business_messaging import agent_config

app = Flask(__name__)
app.config['DEBUG'] = True

# Authenticate with service account
from oauth2client.service_account import ServiceAccountCredentials
scopes = ['https://www.googleapis.com/auth/rcsbusinessmessaging']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    agent_config.PATH_TO_SERVICE_ACCOUNT, scopes=scopes)
app.logger.info(credentials)

http_auth = credentials.authorize(Http())

def emojize(text):
  """
  Utility function to handle emojis within the message text.

  Args:
      text (str): The text that will be sent to the user.

  Returns:
      A :str: Message text after emoji conversion.
  """
  return_text = text

  return_text = emoji.emojize(return_text, use_aliases=True)
  return_text = return_text.replace(':newline:', '\n')
  return_text = return_text.replace(':quote:', '\"')

  return return_text

def send_message_with_body(msisdn, body, message_id):
  """
  Sends a message represented by the given JSON to the given MSISDN.

  Args:
      msisdn (str): The lmsisdn of the user in
          E.164 format, e.g. '+14155555555'.
      body (dict): Object representing the full post body.
      message_id (str): The ID of the message.
  """
  endpoint_url = (agent_config.RBM_BASE_ENDPOINT +
                  'phones/' +
                  msisdn +
                  '/agentMessages?messageId=' +
                  message_id)

  body_string = emojize(json.dumps(body))

  resp, content = http_auth.request(endpoint_url,
                                    method="POST",
                                    body=body_string,
                                    headers={'Content-Type':'application/json'})

  app.logger.info('send_message_with_body()\n\tendpoint_url: ' +
                  endpoint_url+ '\n\tpost_body: ' +
                  body_string + '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  app.logger.info(resp)
  app.logger.info(content)

def send_event_with_body(msisdn, body, message_id):
  """
  Sends an agent event represented by the given JSON to the given MSISDN.

  Args:
      msisdn (str): The lmsisdn of the user in
          E.164 format, e.g. '+14155555555'.
      body (dict): Object representing the full post body.
      message_id (str): The ID of the message.
  """
  endpoint_url = (agent_config.RBM_BASE_ENDPOINT +
                  'phones/' +
                  msisdn +
                  '/agentEvents?eventId=' +
                  message_id)

  body_string = json.dumps(body)

  resp, content = http_auth.request(endpoint_url,
                                    method="POST",
                                    body=body_string,
                                    headers={'Content-Type':'application/json'})

  app.logger.info('send_event_with_body()\n\tendpoint_url: ' +
                  endpoint_url +
                  '\n\tpost_body: ' +
                  body_string +
                  '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  app.logger.info(resp)
  app.logger.info(content)

def send_message_with_body_and_suggestion_chip_list(msisdn, body, suggestion_chip_list, message_id):
  """
  Sends a message represented by the given JSON with the
  additional suggestion chip list JSON to the given MSISDN.

  Args:
      msisdn (str): The msisdn of the user in
          E.164 format, e.g. '+14155555555'.
      body (dict): Object representing the full post body.
      suggestionChipList (list): List of Suggestion objects
          representing a suggestion chip list
          (https://devsite.googleplex.com/rcsbusinessmessaging/rest/v1/phones.agentMessages#Suggestion)
      message_id (str): The ID of the message.
  """
  body['contentMessage']['suggestions'] = suggestion_chip_list
  send_message_with_body(msisdn, body, message_id)

def upload_file(file_url, thumbnail_url=None):
  """
  Uploads a file to the RBM platform.

  Args:
      file_url (str): The publicly available URL of the file.
      thumbnail_url (Optional(str)): The publicly available
          URL of the thumbnail.

  Returns:
      A :str: The file resource identifier in the RBM platform.
  """
  endpoint_url = agent_config.RBM_BASE_ENDPOINT + 'files'

  body = {
      'fileUrl': file_url
  }

  if thumbnail_url:
    body['thumbnailUrl'] = thumbnail_url

  body_string = json.dumps(body)

  resp, content = http_auth.request(endpoint_url,
                                    method="POST",
                                    body=body_string,
                                    headers={'Content-Type':'application/json'})

  app.logger.info('upload_file()\n\tendpoint_url: ' +
                  endpoint_url +
                  '\n\tpost_body: ' +
                  body_string +
                  '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  return json.loads(content)['name']

def make_cap_request(msisdn):
  """
  Makes a RMB capability request check for the msisdn.

  Args:
      msisdn (str): The msisdn of the user in
          E.164 format, e.g. '+14155555555'.

  Returns:
      A :str: The file resource identifier in the RBM platform.
  """
  endpoint_url = (agent_config.RBM_BASE_ENDPOINT +
                  'phones/' +
                  msisdn +
                  '/capability:requestCapabilityCallback')

  body = {
      'requestId': str(uuid.uuid4().int) + "a"
  }

  body_string = json.dumps(body)

  resp = http_auth.request(endpoint_url,
                           method="POST",
                           body=body_string,
                           headers={'Content-Type':'application/json'})

  app.logger.info('make_cap_request()\n\tendpoint_url: ' +
                  endpoint_url +
                  '\n\tpost_body: ' +
                  body_string +
                  '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  return ''

def revoke(msisdn, message_id):
  """
  Removes an exising RBM message.

  Args:
      msisdn (str): The msisdn of the user in
          E.164 format, e.g. '+14155555555'.
      message_id (str): The ID of the message.
  """
  endpoint_url = (agent_config.RBM_BASE_ENDPOINT +
                  'phones/' +
                  msisdn +
                  '/agentMessages/' +
                  message_id)

  resp, content = http_auth.request(endpoint_url, method="DELETE")

  app.logger.info('revoke()\n\tendpoint_url: ' +
                  endpoint_url +
                  '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  return ''


def invite_tester(msisdn):
  """
  Invites a user as a tester of the agent.

  Args:
      msisdn (str): The msisdn of the user in
          E.164 format, e.g. '+14155555555'.
  """
  endpoint_url = (agent_config.RBM_BASE_ENDPOINT +
                  'phones/' +
                  msisdn +
                  '/testers')

  resp, content = http_auth.request(endpoint_url, method="POST")

  app.logger.info('invite_tester()\n\tendpoint_url: ' +
                  endpoint_url +
                  '\n\tresp status: ' +
                  str(resp.status) +
                  '\n\tresp reason: ' +
                  resp.reason)

  return resp

def get_user_response_text(user_event):
  """
  Returns the user response text, either from a direct user text message or
  encoded in a suggested reply postback data
  in the form: '^.*reply:<non-empty user reply>$'.

  Args:
      user_event (dict): The user event as a dictionary.

  Returns:
      A :str: The user response text or None if
          the UserEvent was for something else.
  """
  response_text = None

  if 'text' in user_event:
    response_text = user_event['text']
  elif 'suggestionResponse' in user_event:
    reply_text_regex = re.compile(r'^.*reply:(.+)$')

    # Assumes reply text is encoded in suggested reply
    # in the format '^.*reply:<non-empty user reply>$'
    match = reply_text_regex.match(user_event['suggestionResponse']['postbackData'])

    if match:
      response_text = match.group(1)
  elif 'location' in user_event:  # Special case for location
    response_text = 'location'

  return response_text

def send_read_for_user_event_and_is_typing_if_message(user_event):
  """
  If the given UserEvent represents a user message, sends a READ event for
  the message followed by an IS_TYPING event. Uses the MSISDN in the
  UserEvent. Does nothing if the UserEvent does not represent a user message
  (e.g. is a suggested action postback).

  Args:
      user_event (dict): The user event as a dictionary.
  """

  # Check to see that userEvent was a user message.
  # Note: hacky assumption around format of suggestion reply postback data.
  if get_user_response_text(user_event) and 'messageId' in user_event:
    agent_event = {
        'eventType': 'READ',
        'messageId': user_event['messageId']
    }
    send_event_with_body(user_event['senderPhoneNumber'],
                         agent_event,
                         str(uuid.uuid4().int) + "a")
    send_is_typing_event(user_event['senderPhoneNumber'])

def send_is_typing_event(msisdn):
  """
  Sends IS_TYPING event to the user.

  Args:
      msisdn (str): The msisdn of the user in
          E.164 format, e.g. '+14155555555'.
  """
  agent_event = {
      'eventType': 'IS_TYPING'
  }
  send_event_with_body(msisdn, agent_event, str(uuid.uuid4().int) + "a")
