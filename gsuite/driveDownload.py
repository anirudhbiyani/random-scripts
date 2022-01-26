#!/usr/bin/env python

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors
import io

def main():
   SCOPES = ['https://www.googleapis.com/auth/drive']

   credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes=SCOPES)
   delegated_credentials = credentials.create_delegated('<User Email address whose delegation to be created>')
   service = build('drive','v3', credentials=delegated_credentials)

   fileID = "1vKAr_Izn6qA9A1btULGqRsKqQx8lK3rLoPp4k22tJus"
   store_dir="/Users/aniruddha.biyani/Desktop/"

   request = service.files().export_media(fileId=fileID, mimeType='application/pdf')
   fh = io.FileIO('budget.pdf', 'wb')
   downloader = MediaIoBaseDownload(fh, request)
   done = False
   while done is False:
       status, done = downloader.next_chunk()
       print "Download %d%%." % int(status.progress() * 100)

if __name__ == '__main__':
    main()
