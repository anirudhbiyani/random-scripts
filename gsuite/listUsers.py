#!/usr/bin/env python3

from __future__ import print_function

import datetime, logging, json, logging.handlers
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']

def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    delegate_user = ""
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(delegate_user)
    service = build('admin', 'directory_v1', credentials=delegated_credentials)

    # Call the Admin SDK Directory API
    print('Getting the first 10 users in the domain')
    results = service.users().list(customer='my_customer', maxResults=10, orderBy='email').execute()
    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print(u'{0} ({1})'.format(user['primaryEmail'], user['name']['fullName']))


if __name__ == '__main__':
    main()
