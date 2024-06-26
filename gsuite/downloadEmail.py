#!/usr/bin/env python3

import datetime, logging, json, logging.handlers
from googleapiclient.discovery import build
from google.oauth2 import service_account
from apiclient import errors
import base64
import email

def main():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    delegate_user = ""
    credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.with_subject(delegate_user)
    service = build('gmail','v1', credentials=delegated_credentials)

    message = service.users().messages().list(userId='me').execute()
    print(message)

"""
   store_dir="/Users/aniruddha.biyani/Desktop/"
   response = service.users().messages().list(userId=user_id, q="rfc822msgid:60fd3ef853e6951c66d16cce7.828881ae79.20220913104222.1323eb5116.3270a955@mail223.suw16.rsgsv.net").execute()
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
