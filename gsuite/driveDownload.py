#!/usr/bin/env python3

from __future__ import print_function

import datetime, logging, json, logging.handlers, io
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaIoBaseDownload


def main():
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
    delegate_user = ""
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(delegate_user)
    service = build("drive", "v3", credentials=delegated_credentials)

    fileID = ""
    store_dir = ""

    request = service.files().export_media(fileId=fileID, mimeType="application/pdf")

    fh = io.FileIO(store_dir + "drive.pdf", "wb")

    downloader = MediaIoBaseDownload(fh, request)

    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))


if __name__ == "__main__":
    main()
