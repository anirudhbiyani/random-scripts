#!/usr/bin/env python

"""
You need to define the following environment variable to run
    1. DryRun - This can be either True or False.
    2. Role -
    3. AccountId -
"""

import boto3, json, dateutil.tz
from datetime import datetime
import os

def main():
    dryrun = os.environ['DryRun']
    role = os.environ['Role']
    AccountId = os.environ['DryRun']

    # Connect to AWS APIs
    sts_connection = boto3.client('sts')
    authAccount = sts_connection.assume_role(RoleArn="arn:aws:iam::222222222222:role/role-on-source-account", RoleSessionName="cross_acct_lambda")

    ACCESS_KEY = authAccount['Credentials']['AccessKeyId']
    SECRET_KEY = authAccount['Credentials']['SecretAccessKey']
    SESSION_TOKEN = authAccount['Credentials']['SessionToken']

    # create service client using the assumed role credentials, e.g. IAM
    iclient = boto3.client('iam', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, aws_session_token=SESSION_TOKEN)
    sclient = boto3.client('ses', region_name='us-west-2')
    data = iclient.list_users()
    users = {}
    users_report = []
    userindex = 0
    EMAIL_FROM = 'securitynotification@khoros.com'

    for user in data['Users']:
        userid = user['UserId']
        username = user['UserName']
        users[userid] = username

    for user in users:
        userindex += 1
        user_keys = []
        username = users[user]

        # Add any user to this group if you want to skip this check.
        user_groups = iclient.list_groups_for_user(UserName=username)
        skip = False
        for groupName in user_groups['Groups']:
            if groupName['GroupName'] == 'Excluded':
                print 'Detected that user belongs to ', GROUP_LIST
                skip = True
                continue

        if skip:
            print "Do invalidate Access Key"
            continue

        access_keys = iclient.list_access_keys(UserName=username)['AccessKeyMetadata']
        for access_key in access_keys:
            print access_key

            access_key_id = access_key['AccessKeyId']
            existing_key_status = access_key['Status']
            key_created_date = access_key['CreateDate']

            tz_info = key_created_date.tzinfo
            age = datetime.now(tz_info) - key_created_date
            key_age_str = str(age)
            if 'days' not in key_age_str:
                return 0
            days = int(key_age_str.split(',')[0].split(' ')[0])

            # we only need to examine the currently Active and about to expire keys
            if existing_key_status == "Inactive":
                key_state = 'key is already in an INACTIVE state'
                key_info = {'accesskeyid': userid, 'age': age, 'state': key_state, 'changed': False}
                user_keys.append(key_info)
                continue

            if user == 'root':
                client.update_access_key(UserName=username, AccessKeyId=access_key_id, Status="Inactive")
            else:
                continue

            key_state = ''
            key_state_changed = False
            if days < 90:
                key_state = 'keyInRange'
            elif days == 120:
                key_state = 'firstWaring'
            elif days == 150:
                key_state = 'secondWarning'
            elif days >= 180:
                key_state = 'expired'
                if dryrun = False:
                    client.update_access_key(UserName=username, AccessKeyId=access_key_id, Status="Inactive")
                    email_to = str(username) + '@khoros.com'
                    data = 'The Access Key [%s] belonging to User [%s] has been automatically deactivated due to it being %s days old' % (userid, username, age)
                    response = sclient.send_email(Source=EMAIL_FROM, Destination={'ToAddresses': [email_to]}, Message={'Subject': {'Data': 'Deactivation of Access Key: %s' % userid}, 'Body': { 'Text': { 'Data': data}}})
                    key_state_changed = True
                else:
                    continue

            key_info = {'accesskeyid': userid, 'age': age, 'state': key_state, 'changed': key_state_changed}
            user_keys.append(key_info)

        report = {'userid': userindex, 'username': username, 'keys': user_keys}
        users_report.append(report)

    finished = str(datetime.now())
    deactivated_report = {'reportdate': finished, 'users': users_report}
    data = 'AWS IAM Access Key Rotation Lambda Function (cron job) finished successfully at %s \n \n Deactivation Report:\n%s' % (finished, json.dumps(deactivated_report, indent=4, sort_keys=True))
    response = sclient.send_email(Source=EMAIL_FROM, Destination={'ToAddresses': 'infosec@khoros.com'}, Message={'Subject': {'Data': 'AWS IAM Access Key Rotation - Lambda Function'}, 'Body': { 'Text': { 'Data': data}}})

if __name__ == "__main__":
    main()
