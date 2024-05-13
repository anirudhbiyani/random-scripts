from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import requests
import logging
import datetime
import pandas as pd


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "" # Spreadsheet ID
RANGE_NAME = "OncallSheet!A1:F"


def send_notification(primary_slack_id, secondary_slack_id):
    primaryid = primary_slack_id
    secondaryid = secondary_slack_id
    msg = "<@{0}> is primary on call and <@{1}> is secondary oncall for today.".format(
        primaryid, secondaryid
    )
    # Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
    webhook_url = "" # slack webhook URL
    slack_data = {"text": msg}

    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code != 200:
        err = "Request to slack returned an error %s, the response is:\n%s" % (
            response.status_code,
            response.msg,
        )
        logging.error(err)


def send_notification_week(primary_slack_id, secondary_slack_id):
    primaryid = primary_slack_id
    secondaryid = secondary_slack_id
    msg = "<@{0}> is primary on call and <@{1}> is secondary oncall for this week.".format(
        primaryid, secondaryid
    )
    # Set the webhook_url to the one provided by Slack when you create the webhook at https://my.slack.com/services/new/incoming-webhook/
    webhook_url = "https://hooks.slack.com/services/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"
    slack_data = {"text": msg}

    response = requests.post(
        webhook_url,
        data=json.dumps(slack_data),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code != 200:
        err = "Request to slack returned an error %s, the response is:\n%s" % (
            response.status_code,
            response.msg,
        )
        logging.error(err)


def weekbot():
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    if week_num > 7:
        week_num = week_num % 7
    return week_num


def main():
    creds = None
    dict = {
        "0": "Monday",
        "1": "Tuesday",
        "2": "Wednesday",
        "3": "Thursday",
        "4": "Friday",
        "5": "Saturday",
        "6": "Sunday",
    }
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    )
    values = result.get("values", [])
    today = datetime.datetime.today().weekday()
    day_num = str(today)
    if not values:
        print("No data found.")
    df = pd.DataFrame(values[1:], columns=values[0])
    day = []
    day.append(dict[day_num])
    id = df[df.Day.isin(day)]
    primary_slack_id = id["Primary Oncall Slack ID"]
    primary_slack_id = primary_slack_id.to_string(index=False)
    secondary_slack_id = id["Secondary Oncall Slack ID"]
    secondary_slack_id = secondary_slack_id.to_string(index=False)
    # send_notification(primary_slack_id, secondary_slack_id)
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    # print(week_num)
    week_max = df.Week.max()
    if int(week_max) < int(week_num):
        week_num = int(week_num) % int(week_max)
        if week_num == 0:
            week_num = week_num + 1
        else:
            week_num = week_num
    else:
        week_num = week_num

    week_id = df[df.Week == str(week_num)]
    #print(week_id)
    #print(week_num)
    week_no = week_id["Week"].to_string(index=False)
    psid = week_id["Primary Oncall Slack ID"].to_string(index=False)
    ssid = week_id["Secondary Oncall Slack ID"].to_string(index=False)
    #print(psid, ssid, week_no)
    week_max = df.Week.max()
    if int(week_max) < int(week_no):
        week_comp = week_max
    else:
        week_comp = int(week_max) % int(week_no)
    # print(week_comp)
    send_notification_week(psid, ssid)


if __name__ == "__main__":
    main()
