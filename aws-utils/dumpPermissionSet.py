#!/usr/bin/env python3

# pylint: disable=invalid-name,line-too-long

import boto3, yaml, os, sys

def main():
    account = boto3.Session(profile_name=sys.argv[1]).client('sts', region_name='us-west-2').get_caller_identity().get('Account')
    print(account)
    #account = boto3.client('sts').get_caller_identity().get('Account')
    if account == '758101156825':
        environment = "/dev"
    elif account == '441965525732':
        environment = ""
    else:
        sys.exit()

    org = boto3.Session(profile_name=sys.argv[1]).client('organizations', region_name='us-west-2')
    ssoadmin = boto3.Session(profile_name=sys.argv[1]).client('sso-admin', region_name='us-west-2')
    identity = boto3.Session(profile_name=sys.argv[1]).client('identitystore', region_name='us-west-2')

    accountList = []
    permissionsetList = []

    instancearn = ssoadmin.list_instances()['Instances'][0]['InstanceArn']
    instancestoreId = ssoadmin.list_instances()['Instances'][0]['IdentityStoreId']
    response = ssoadmin.list_permission_sets(InstanceArn=instancearn)

    allaccount = {}
    response = org.list_accounts()
    for i in response['Accounts']:
        allaccount[i['Name']] = i['Id']

    while 'NextToken' in response:
        response = org.list_accounts(NextToken=response['NextToken'])
        for i in response['Accounts']:
            allaccount[i['Name']] = i['Id']
    print(allaccount)
    response = ssoadmin.list_permission_sets(InstanceArn=instancearn)
    for x in response['PermissionSets']:
        permissionsetList.append(x)

    while 'NextToken' in response:
        response = ssoadmin.list_permission_sets(InstanceArn=instancearn, NextToken=response['NextToken'])
        for x in response['PermissionSets']:
            permissionsetList.append(x)

    for x in permissionsetList:
        accountList = []
        permissionsetmappings = {}

        permissionsetname = ssoadmin.describe_permission_set(InstanceArn=instancearn, PermissionSetArn=x)['PermissionSet']['Name']

        filename = f'permissionset/{permissionsetname}.yaml'
        file = open(filename, 'w+')

        response = ssoadmin.list_accounts_for_provisioned_permission_set(InstanceArn=instancearn, PermissionSetArn=x)
        for account in response['AccountIds']:
            accountList.append(account)

        while 'NextToken' in response:
            response = ssoadmin.list_accounts_for_provisioned_permission_set(InstanceArn=instancearn, PermissionSetArn=x, NextToken=response['NextToken'])
            for account in response['AccountIds']:
                accountList.append(account)

        for i in accountList:
            print(i)
            principalList = []
            accountName = list(allaccount.keys())[list(allaccount.values()).index(i)]
            print(accountName)
            principal = ssoadmin.list_account_assignments(InstanceArn=instancearn, AccountId=i, PermissionSetArn=x)['AccountAssignments']

            for j in principal:
                if j['PrincipalType'] == 'USER':
                    identityname = identity.describe_user(IdentityStoreId=instancestoreId,UserId=j['PrincipalId'])
                    print(identityname)
                    principalList.append(identityname['UserName'])
                else:
                    print(j)
                    identityname = identity.describe_group(IdentityStoreId=instancestoreId,GroupId=j['PrincipalId'])
                    print(identityname)
                    principalList.append(identityname['DisplayName'])
            permissionsetmappings[accountName] = principalList

        yaml.dump(permissionsetmappings, file, sort_keys=True, default_flow_style=False)
        file.close()

if __name__ == '__main__':
    main()
