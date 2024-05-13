#!/usr/bin/env python

import datetime, logging, json, logging.handlers
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors

def main():
   SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

   delegate_user = ""
   credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
   delegated_credentials = credentials.create_delegated(delegate_user)
   service = build('admin', 'directory_v1', credentials=delegated_credentials)

   results = service.users().list(domain='khoros.com', projection='custom', customFieldMask = 'SSO', orderBy='email').execute()
   users = results.get('users', [])
   page = results.get('nextPageToken')
   pa = page

   for user in users:
       if 'customSchemas' in user:
           print(u'{0} {1}'.format(user['name'], user['customSchemas']))

   while(page):
       npage = service.users().list(domain='khoros.com', projection='custom', customFieldMask = 'SSO', pageToken=pa).execute()
       pa = npage.get('nextPageToken')
       l = npage.get('users', [])
       if not npage:
           pass
       else:
           for j in l:
               if 'customSchemas' in j:
                   print(u'{0} {1}'.format(j['name'], j['customSchemas']))
       pa = npage.get('nextPageToken')

if __name__ == '__main__':
  main()
