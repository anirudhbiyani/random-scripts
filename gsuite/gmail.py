#!/usr/bin/env python3

import datetime, logging, json, logging.handlers
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors
import base64
import email

def main():
    user_id = ''

    SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://www.googleapis.com/auth/admin.reports.usage.readonly', 'https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/activity', 'https://www.googleapis.com/auth/admin.directory.user.security', 'https://www.googleapis.com/auth/admin.directory.user.readonly', 'https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.readonly']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.with_subject(user_id)
    service = build('gmail','v1', credentials=delegated_credentials)

    message = service.users().messages().list(userId='saksham.tushar@gcred.club').execute()
    print(message)
"""
#   response = service.users().messages().list(userId=user_id, q="rfc822msgid:CAFCSPomP0bmKSAd2Kwz7bO=KLfmQET-NV6F3Vm=orCoRQP_65A@mail.gmail.com").execute()
   print response
   if 'messages' in response:
       messages.extend(response['messages'])
       msg_id = str(messages[0].get('id'))
 #  print msg_id
   message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
 #  print message
   msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
   mime_msg = email.message_from_string(msg_str)
   print mime_msg

   for part in message['payload']['parts']:
       if 'data' in part['body']:
           data=part['body']['data']
       else:
           att_id=part['body']['attachmentId']
           att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
           data=att['data']
           file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
           #path = prefix+part['filename']
           with open('/Users/aniruddha.biyani/Desktop/test', 'w') as f:
               f.write(file_data)
"""
if __name__ == '__main__':
    main()
