#!/usr/bin/env python

import datetime, logging
from logging.handlers import SysLogHandler
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials

def main():
    SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://www.googleapis.com/auth/admin.reports.audit.readonly',  'https://www.googleapis.com/auth/admin.reports.usage.readonly', 'https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/gmail.metadata', 'https://www.googleapis.com/auth/activity', 'https://www.googleapis.com/auth/admin.directory.user.security', 'https://www.googleapis.com/auth/admin.directory.user.readonly',       'https://www.googleapis.com/auth/gmail.readonly']

    # Authenticate and construct service.
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.create_delegated('aniruddha.biyani@spredfast.com')
    auditservice = build('admin','reports_v1', credentials=delegated_credentials)

    # Setup the logging service
    logger = logging.getLogger()
    syslog = SysLogHandler(address='/var/run/syslog', facility='local5')
    formatter = logging.Formatter('%(asctime)s %(message)r', datefmt='%m/%d/%Y %I:%M:%S')
    syslog.setFormatter(formatter)
    logger.addHandler(syslog)

    # Querying the API to pull the logs
    results = auditservice.activities().list(userKey='all', applicationName='admin', startTime=str((datetime.datetime.utcnow() - datetime.timedelta(hours=48)).isoformat() + 'Z'), endTime=str(datetime.datetime.utcnow().isoformat()+'Z')).execute()
    logs = results.get('items', [])
    page = results.get('nextPageToken')
    pa = page

    print results
    # Checking if the result exists and print if they do.
    if not results:
        print 'No result found.'
    else:
        for i in logs:
            print i
            logger.info(i)

    # Looping over the paginated results.
    while(page):
        print '#' * 50
        npage = auditservice.activities().list(userKey='all', applicationName='admin', pageToken=pa).execute()
        pa = npage.get('nextPageToken')
        l = npage.get('items', [])
        if not npage:
            print 'No result found.'
        else:
            for j in l:
                logger.info(j)
        pa = npage.get('nextPageToken')

if __name__ == '__main__':
    main()

