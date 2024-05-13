#!/usr/bin/env python3

import requests
import json
import os
import time
import datetime
import jira
import ast
from elasticsearch import Elasticsearch
from requests.auth import HTTPBasicAuth


def sendToJIRA(alert):
    tix = ast.literal_eval(alert)
    url = "https://dreamplug.atlassian.net/rest/api/3/issue"
    auth = HTTPBasicAuth( "<JIRA User>", "<JIRA Token>")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "fields": {
            "description": {
                "content": [
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "json"},
                        "content": [{"text": "placeholder", "type": "text"}],
                    }
                ],
                "type": "doc",
                "version": 1,
            },
            "issuetype": {"id": "10495"},
            "labels": ["CRED", "GoogleWorkspace"],
            "priority": {"id": "4"},
            "project": {"id": "11301"},
            "summary": "Google Workspace - Bulk file download",
        }
    }
    severity = tix["_source"]["context.rule.severity"]
    if severity.lower() == "low":
        payload["fields"]["priority"]["id"] = "4"
    elif severity.lower() == "medium":
        payload["fields"]["priority"]["id"] = "3"
    elif severity.lower() == "high":
        payload["fields"]["priority"]["id"] = "2"
    elif severity.lower() == "critical":
        payload["fields"]["priority"]["id"] = "1"
    else:
        payload["fields"]["priority"]["id"] = "2"

    payload["fields"]["summary"] = tix["_source"]["rule.name"]

    event_tags = tix["_source"]["rule.tags"].replace(" ", "").split(",")
    payload["fields"]["labels"] = [i for i in event_tags if not ("__" in i)]

    payload["fields"]["description"]["content"][0]["content"][0]["text"] = tix[
        "_source"
    ]["context.alerts"]

    payload = json.dumps(payload)
    response = requests.request("POST", url, data=payload, headers=headers, auth=auth)

    """
def crossChecker():
    # checking for missed alerts in last 1 hour
    if hour_counter == 0:
      es_hourly_data = fetch(ELK_HOST, ELK_ID, ELK_KEY, '1h')
      if es_hourly_data != 0:
        print(f"[+] {datetime.datetime.now()}: Checking for missed alerts in last 1hr")
        hourly_events = es_hourly_data['hits']['hits']
        for hourly_event_details in hourly_events:
            if hourly_event_details['_id'] not in raised_alert_ids:
                if SEND_TO_HIVE == 'true':
                  try:
                    print(f"[+] {datetime.datetime.now()}: Sending missed alert (id: {hourly_event_details['_id']}) to TheHive")
                    send_single_event_to_hive(HIVE_URL, HIVE_KEY, hourly_event_details)
                  except Exception as e:
                    print(f'[!] {datetime.datetime.now()}: Exception occurred while sending missed alert to Hive: {e}')
                    print(f"[x] {datetime.datetime.now()}: Mised Failed! Exitting, STATUS - 500")
                    # return 500

                    print(f"[+] {datetime.datetime.now()}: Alert raised successfully - Exitting, STATUS - 200")
                    # return 200
  """


def main():
    hour_counter = 0
    raised_alert_ids = []

    try:
        ELK_HOST = os.environ["ELK_HOST"]
        ELK_ID = os.environ["ELK_ID"]
        ELK_KEY = os.environ["ELK_KEY"]
        FETCH = os.environ["FETCH"]
    except Exception as e:
        print(
            f"[!] {datetime.datetime.now()}: Exception occured while reading env variables: {e}"
        )

    while True:
        mod = 60 // int(FETCH[0])
        hour_counter = (hour_counter + 1) % mod

        # fetch alerts
        elastic_client = Elasticsearch(
            hosts=ELK_HOST,
            ssl_assert_fingerprint="2F:B9:95:85:2D:F4:26:14:BB:1C:63:30:B1:F5:83:23:44:A5:66:9C:5A:E9:20:96:D9:67:7B:95:76:79:82:AB",
            api_key=(ELK_ID, ELK_KEY),
        )
        from_time = f"now-{FETCH}"
        query = {"range": {"@timestamp": {"gte": from_time, "lt": "now"}}}

        print(f"[+] {datetime.datetime.now()}: Fetching alerts from last {FETCH}")
        elastic_data = dict(
            elastic_client.search(index="siem-alerts*", size=1000, query=query)
        )
        print(
            f'{datetime.datetime.now()}: Total number of alerts fetched: {len(elastic_data["hits"]["hits"])}'
        )
        if len(elastic_data["hits"]["hits"]) != 0:
            for i in elastic_data["hits"]["hits"]:
                sendToJIRA(str(i))
        else:
            print(f"{datetime.datetime.now()}: No alerts found, exiting.")

        # sleep for FETCH*60 seconds
        time.sleep(int(FETCH[0]) * 60)


if __name__ == "__main__":
    main()
