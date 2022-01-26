#!/usr/bin/env python

import datetime, time
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials

__author__ = "Aniruddha Biyani"
__version__ = "1.0.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudbiyani.com"
__status__ = "Active"

# Call the Admin SDK Reports API got Login events last 10 for all user

def main():
    adminUser = "" # UserID of the admin user
    orgDomain = "" # Domain of your organization

    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(adminUser)
    loginservice = build('admin', 'reports_v1', credentials=delegated_credentials)

    print('Getting the last 10 login events')
    results = loginservice.activities().list(userKey='all', applicationName='login', maxResults=10).execute()
    activities = results.get('items', [])

    if not activities:
        print('No logins found.')
    else:
        print('Logins:')
        for activity in activities:
            print(u'{0}: {1} ({2})'.format(activity['id']['time'],activity['actor']['email'], activity['events'][0]['name']))


if __name__ == '__main__':
    main()
