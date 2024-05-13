#!/usr/bin/env python3

import datetime, logging, json, logging.handlers
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials

def main():
    SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://www.googleapis.com/auth/admin.reports.usage.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/admin.directory.user.readonly', 'https://www.googleapis.com/auth/admin.directory.group.readonly']

    delegate_user = ""

    # Authenticate and construct service.
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(delegate_user)
    auditservice = build('admin','reports_v1', credentials=delegated_credentials)

    # Querying the API to pull the logs
    results = auditservice.activities().list(userKey='all', applicationName='admin', startTime=str((datetime.datetime.utcnow() - datetime.timedelta(hours=72)).isoformat() + 'Z'), endTime=str(datetime.datetime.utcnow().isoformat()+'Z')).execute()
    logs = results.get('items', [])
    page = results.get('nextPageToken')
    pa = page

    # Checking if the result exists and print if they do.
    if not results:
        pass
    else:
        for i in logs:
	#    logger.info(json.dumps(i, ensure_ascii=False))
            print(i)

    # Looping over the paginated results.
    while(page):
        npage = auditservice.activities().list(userKey='all', applicationName='admin', pageToken=pa).execute()
        pa = npage.get('nextPageToken')
        l = npage.get('items', [])
        if not npage:
            pass
        else:
            for j in l:
                #logger.info(json.dumps(j, ensure_ascii=False))
                print(j)
        pa = npage.get('nextPageToken')

if __name__ == '__main__':
    main()
