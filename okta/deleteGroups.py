#!/usr/bin/env python3

import requests, sys, os

def main():
    OKTA_TOKEN=os.environ['OKTA_TOKEN']
    OKTA_HOST="fireeye.okta.com"
    headers = {
        "Accept": "application/json",
        'Content-type': 'application/json',
        'Authorization': 'SSWS ' + OKTA_TOKEN
    }

    oktagroups = []
    # Get all the Groups that are assigned to "AWS Single Sign On" app in Okta
    url = f'https://{OKTA_HOST}/api/v1/groups?q={sys.argv[1]}&limit=200&filter=type+eq+%22OKTA_GROUP%22'
    response = requests.get(url, headers=headers)
    for value in response.json():
        application = value['_links']['apps']['href']
        gresponse = requests.get(application, headers=headers)
        if not gresponse.json():
            oktagroups.append(value['id'])
        else:
            act = False
            for i in gresponse.json():
                if i['status'] == "ACTIVE":
                    act = True
            if act == False:
                oktagroups.append(value['id'])

    for gid in oktagroups:
        url = f"https://{OKTA_HOST}/api/v1/groups/{gid}"
        result = requests.get(url, headers=headers)
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(result.json()['profile']['name'] + ' Okta Group deleted successfully.')
        else:
            print(result.json()['profile']['name'] + ' Okta Group could not be deleted.')

if __name__ == '__main__':
    main()
