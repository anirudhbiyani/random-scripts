#!/usr/bin/env python3

# pylint: disable=line-too-long,invalid-name,global-variable-undefined,missing-function-docstring,missing-module-docstring

import os, requests, sys, json, re

def getGroupID(group_name):
    url = f'https://{host}/api/v1/groups?q={group_name}&limit=100&filter=type+eq+%22OKTA_GROUP%22'
    response = requests.get(url, headers=headers)
    if len(response.json()) != 1:
        sys.exit("Multiple or None Groups found with this prefix in Okta.")
    else:
        result = response.json()
        return result[0]['id']

def getUserID(user_login):
    # GET /api/v1/users
    url = f'https://{host}/api/v1/users/{user_login}'
    response = requests.get(url, headers=headers)
    result = json.loads(response.text)
    if result['status'] == 'ACTIVE':
        return None
    else:
        return result['id']

def getMembers(groupid):
    group_membership = []
    url = "https://fireeye.okta.com/api/v1/groups/" + groupid + "/users"
    response = requests.get(url, headers=headers)
    result = response.json()
    for x in range(len(result)):
        group_membership.append(result[x]['profile']['login'])

    return group_membership

def removeMember(groupid, userid):
    # DELETE /api/v1/groups/${groupId}/users/${userId}
    url = f'https://{host}/api/v1/groups/{groupid}/users/{userid}'
    response = requests.delete(url, headers=headers)
    return response.status_code

def main():
    # Getting the OKTA_TOKEN from environment variable
    global token
    global host
    global headers
    token = os.environ['OKTA_TOKEN'] # Move this into AWS Parameter Store
    host = os.environ['host']
    headers = {
        "Accept": "application/json",
        'Content-type': 'application/json',
        'Authorization': 'SSWS ' + token
    }
    oktagroups = []
    members=[]

    # Get all the Groups that are assigned to "AWS Single Sign On" app in Okta
    url = f'https://{host}/api/v1/apps/0oa1hixcsycHOZvCK1d8/groups?limit=100'
    response = requests.get(url, headers=headers)
    for value in response.json():
        groupname = value['_links']['group']['href']
        gresponse = requests.get(groupname, headers=headers)
        r = gresponse.json()['profile']['name']
        oktagroups.append(r)
    if "after" in response.headers['link']:
        nextlink = re.search("<(.*?)>", response.headers['link'].split(',')[1])
        nexturl = nextlink.group(0)[:-1][1:]

    while nexturl is not None:
        response = requests.get(nexturl, headers=headers)
        for value in response.json():
            groupname = value['_links']['group']['href']
            gresponse = requests.get(groupname, headers=headers)
            r = gresponse.json()['profile']['name']
            oktagroups.append(r)
        if "next" in response.headers['link']:
            nextlink = re.search("<(.*?)>", response.headers['link'].split(',')[1])
            nexturl = nextlink.group(0)[:-1][1:]
        else:
            nexturl = None

    print(oktagroups)

    for x in oktagroups:
        gid = getGroupID(x)
        members = getMembers(gid)
        for i in members:
            uid = getUserID(i)
            if uid == None:
                continue
            else:
                code = removeMember(gid, uid)
                if code == 204:
                    print(i + ' successfully removed from group ' + x)
                else:
                    print(i + ' could not be removed from group ' + x)

if __name__ == '__main__':
    main()
