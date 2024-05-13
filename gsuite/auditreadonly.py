#!/usr/bin/env python3

import datetime, time
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials

def main():
    SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://www.googleapis.com/auth/admin.reports.audit.readonly',  'https://www.googleapis.com/auth/admin.reports.usage.readonly', 'https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/gmail.metadata', 'https://www.googleapis.com/auth/activity', 'https://www.googleapis.com/auth/admin.directory.user.security', 'https://www.googleapis.com/auth/admin.directory.user.readonly',  	'https://www.googleapis.com/auth/gmail.readonly']

    delegate_user = ""

    # Authenticate and construct service.
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(delegate_user)

    # Call the Admin SDK Reports API for Administrator activity
    auditservice = build('admin','reports_v1', credentials=delegated_credentials)
    r = auditservice.activities().list(userKey='all', applicationName='admin', startTime=str((datetime.datetime.utcnow() - datetime.timedelta(hours=6)).isoformat() + 'Z'), endTime=str(datetime.datetime.utcnow().isoformat()+'Z')).execute()
    print r
    results = r.get('items', [])

    if not results:
        print('No logins found.')
    else:
        print('Logins:')
        for i in results:
            print(u'{0}: {1} ({2})'.format(i['id']['time'],i['actor']['email'], i['events'][0]['name']))

    # Call the Admin SDK Reports API got Login events for all user
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
