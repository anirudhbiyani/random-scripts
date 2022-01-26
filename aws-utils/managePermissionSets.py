#!/usr/bin/env python3

# pylint: disable=invalid-name,line-too-long

import boto3, yaml, os

def diff(list1, list2):
    return list(list(set(list1)-set(list2)))

def main():
    lambda_handler(event, None)

def lambda_handler(event, context):

    bucket_name = os.environ['BUCKET_NAME']
    print(bucket_name)

    org = boto3.client('organizations', region_name='us-west-2')
    ssoadmin = boto3.client('sso-admin', region_name='us-west-2')
    identity = boto3.client('identitystore', region_name='us-west-2')
    s3_client = boto3.client('s3', region_name='us-west-2')
    instancearn = ssoadmin.list_instances()['Instances'][0]['InstanceArn']
    instancestoreId = ssoadmin.list_instances()['Instances'][0]['IdentityStoreId']

    permissionsetList = []
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


    if 'Records' in event:
        f = event['Records'][0]['s3']['object']['key']
        permissionsetname = [os.path.splitext(os.path.basename(f))[0]]
        print(permissionsetname)
        for i in permissionsetList:
            if permissionsetname == ssoadmin.describe_permission_set(InstanceArn=instancearn, PermissionSetArn=i)['PermissionSet']['Name']:
                permissionsetList = [i]
            else:
                continue

    #permissionsetList = ['arn:aws:sso:::permissionSet/ssoins-7907ed5f6d19fdbb/ps-648f51c7b057b415']
    print(permissionsetList)

    for x in permissionsetList:
        accountList = []
        templist = []
        permissionsetname = ssoadmin.describe_permission_set(InstanceArn=instancearn, PermissionSetArn=x)['PermissionSet']['Name']
        print(f'Running for {permissionsetname} with id {x}')

        filename = f'/tmp/{permissionsetname}.yaml'
        f = f'permissionset/{permissionsetname}.yaml'

        print(f)
        print(filename)
        s3_client.download_file(bucket_name, f, filename)

        if os.path.exists(filename):
            file = open(filename, 'r+')
            result = yaml.load(file, Loader=yaml.FullLoader)
        else:
            continue

        yamlAccount = result.keys()
        for i in yamlAccount:
            templist.append(allaccount[i])
        yamlAccount = templist

        response = ssoadmin.list_accounts_for_provisioned_permission_set(InstanceArn=instancearn, PermissionSetArn=x)
        for account in response['AccountIds']:
            accountList.append(account)

        while 'NextToken' in response:
            response = ssoadmin.list_accounts_for_provisioned_permission_set(InstanceArn=instancearn, PermissionSetArn=x, NextToken=response['NextToken'])
            for account in response['AccountIds']:
                accountList.append(account)

        print(accountList)

        for i in result.keys():
            principalList = []
            accountNumber = allaccount.get(i)

            # This is to update any groups or users for a particular permissionset in a particular account.
            groupList = result.get(i)
            principal = ssoadmin.list_account_assignments(InstanceArn=instancearn, AccountId=accountNumber, PermissionSetArn=x)['AccountAssignments']

            for j in principal:
                if j['PrincipalType'] == 'USER':
                    identityname = identity.describe_user(IdentityStoreId=instancestoreId,UserId=j['PrincipalId'])
                    principalList.append(identityname['UserName'])
                else:
                    identityname = identity.describe_group(IdentityStoreId=instancestoreId,GroupId=j['PrincipalId'])
                    principalList.append(identityname['DisplayName'])

            groupstoAdd = diff(groupList, principalList)
            print("Principal to add - ")
            print(groupstoAdd)
            for p in groupstoAdd:
                if p.endswith('@fireeye.com'):
                    u = identity.list_users(IdentityStoreId=instancestoreId, Filters=[{'AttributePath': 'UserName','AttributeValue': p},])['Users'][0]['UserId']
                    ssoadmin.create_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='USER', PrincipalId=u)
                else:
                    g = identity.list_groups(IdentityStoreId=instancestoreId, Filters=[{'AttributePath': 'DisplayName','AttributeValue': p},])['Groups'][0]['GroupId']
                    ssoadmin.create_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='GROUP', PrincipalId=g)

            groupstoRemove = diff(principalList, groupList)
            print("Principal to remove - ")
            print(groupstoRemove)
            for j in groupstoRemove:
                mapping = ssoadmin.list_account_assignments(InstanceArn=instancearn, AccountId=accountNumber, PermissionSetArn=x)['AccountAssignments']
                for r in mapping:
                    if r['PrincipalType'] == 'USER':
                        ssoadmin.delete_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='USER',PrincipalId=r['PrincipalId'])
                    else:
                        ssoadmin.delete_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='GROUP',PrincipalId=r['PrincipalId'])

        # This is to check and add any new account for a particular permissionset.
        accountstoadd = diff(yamlAccount, accountList)
        print('AWS Accounts to add - ')
        print(accountstoadd)
        for q in accountstoadd:
            accountname=list(allaccount.keys())[list(allaccount.values()).index(q)]
            principalname = result.get(accountname)
            print(principalname)
            if principalname[0].endswith('@fireeye.com'):
                u = identity.list_users(IdentityStoreId=instancestoreId, Filters=[{'AttributePath': 'UserName','AttributeValue': principalname[0]},])['Users'][0]['UserId']
                ssoadmin.create_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='USER', PrincipalId=u)
            else:
                g = identity.list_groups(IdentityStoreId=instancestoreId, Filters=[{'AttributePath': 'DisplayName','AttributeValue': principalname[0]},])['Groups'][0]['GroupId']
                ssoadmin.create_account_assignment(InstanceArn=instancearn,TargetId=accountNumber,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='GROUP', PrincipalId=g)

        # This is to check and remove any new account for a particular permissionset.
        accountstoremove = diff(accountList, yamlAccount)
        print('AWS Accounts to remove - ')
        print(accountstoremove)
        for q in accountstoremove:
            mapping = ssoadmin.list_account_assignments(InstanceArn=instancearn, AccountId=q, PermissionSetArn=x)['AccountAssignments']
            for j in mapping:
                if j['PrincipalType'] == 'USER':
                    ssoadmin.delete_account_assignment(InstanceArn=instancearn,TargetId=q,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='USER',PrincipalId=j['PrincipalId'])
                else:
                    ssoadmin.delete_account_assignment(InstanceArn=instancearn,TargetId=q,TargetType='AWS_ACCOUNT',PermissionSetArn=x,PrincipalType='GROUP',PrincipalId=j['PrincipalId'])

        file.close()

if __name__ == '__main__':
    main()
