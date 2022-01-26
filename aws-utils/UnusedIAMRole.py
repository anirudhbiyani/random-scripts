import boto3
import json
import os
import logging
from datetime import datetime, timezone
from botocore.exceptions import ClientError
import csv
import io
import time


try:
    log_level = os.environ['LOG_LEVEL']
    print('log_level: ' + log_level)
except KeyError as error:
    print('LOG_LEVEL not provided. So use INFO level...')
    log_level = logging.INFO

logger = logging.getLogger('iam_unused_roles')
logger.setLevel(log_level)


try:
    notification_type = os.environ['NOTIFICATION_TYPE']
    print('notification_type: ' + notification_type)
except KeyError as error:
    print('NOTIFICATION_TYPE not provided. So use INFO level...')


try:
    athena_db = os.environ['ATHENA_DB']
    logger.debug('athena_db: ' + athena_db)
except KeyError as error:
    logger.error('Please set environment variable ATHENA_DB...')
    raise EnvironmentError('ATHENA_DB is not set as environment variable...')

try:
    s3_bucket = os.environ['S3_BUCKET']
    logger.debug('s3_bucket: ' + s3_bucket)
except KeyError as error:
    logger.error('Please set environment variable S3_BUCKET...')
    raise EnvironmentError('S3_BUCKET is not set as environment variable...')




now = datetime.now()
dt_folder = now.strftime("%d_%m_%Y")

sts_client = boto3.client('sts')

now = datetime.now()

dt_folder = now.strftime("%d_%m_%Y")

#os.mkdir('unused_roles')
os.mkdir('/tmp/unused_roles/')
accounts_summary = {}
summary_report = []
roles_tobe_deleted=[]

def store_notification_in_s3(report_str,name, acc_name, year, month, day):
    try:
        # config = Config(connect_timeout=20, read_timeout=20)
        s3_client = boto3.client('s3')
        logger.info('After S3 Client creation ***********')
        s3_client.put_object(Body=report_str.encode(), Bucket='awssec-iam-report',
                             Key='report/year=' + str(year) + '/month=' + str(month) + '/day=' + str(day) + '/' +acc_name+'_'+name + '.json')
        return True
    except ClientError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
    return False



def store_report_in_s3(tmp_file,name, acc_name):
    try:
        # config = Config(connect_timeout=20, read_timeout=20)
        # s3_client = boto3.client('s3')
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket('awssec-iam-report')
        logger.info('After S3 resource creation ***********')
        key='attachment_files'+'/'+dt_folder+'/'+name+'/'+acc_name+ '/' +acc_name+'_'+name + '.csv'
        bucket.upload_file(tmp_file, key)
        # s3_client.put_object(Body=report_str.encode(), Bucket='awssec-iam-report',
        #                      Key='report/year=' + str(year) + '/month=' + str(month) + '/day=' + str(day) + '/' +acc_name+'_'+name + '.json')
        return True
    except ClientError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
    return False


def refreshAthenaPartitions(table_name):
    try:
        logger.info("In refresh Partitions" + athena_db)
        at_client = boto3.client('athena')
        config = {'OutputLocation': 's3://' + s3_bucket + '/refresh'}
        refresh_query = 'MSCK REPAIR TABLE ' + table_name
        queryStart = at_client.start_query_execution(QueryString=refresh_query,
                                                     QueryExecutionContext={'Database': athena_db},
                                                     ResultConfiguration=config)
        execution_id = queryStart['QueryExecutionId']
        state = 'RUNNING'
        max_execution = 20

        while (max_execution > 0 and state in ['RUNNING']):
            logger.debug('In execution check While ***** :' + str(max_execution))
            max_execution = max_execution - 1
            response = at_client.get_query_execution(QueryExecutionId=execution_id)

            if 'QueryExecution' in response and \
                    'Status' in response['QueryExecution'] and \
                    'State' in response['QueryExecution']['Status']:
                state = response['QueryExecution']['Status']['State']

                logger.info('Refresh Response status :' + str(state))
                if state == 'FAILED':
                    logger.info("Reached Failed")
                    logger.info(response['QueryExecution']["Q"])
                    return False
                elif state == 'SUCCEEDED':
                    return True
                else:
                    logger.info('Reached Else, Printing State : ')
                    logger.info(state)

            time.sleep(1)
    except ClientError as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
    return False



def lambda_handler(event, context):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='https://dynamodb.us-west-2.amazonaws.com')
        accounts_table = dynamodb.Table('feye-accounts')
        response = accounts_table.scan()
    except ClientError as e:
        logger.exception(e)
    else:
        if response and 'Items' in response:
            for each_account in response['Items']:
                # sp_arr = each_account.split()
                account = each_account['account_name']
                account_id = each_account['account_id']

                # We can not connect to Gamma from zulu0 account
                if 'gamma' in account:
                    continue

                if not account == 'delta5':
                    continue


                # os.mkdir('unused_roles/'+dt_folder+'/'+account)
                # logging.basicConfig(filename='unused_roles/'+dt_folder+'/'+account+'/unused_role_permissions.log', level=logging.INFO)
                each_account_count = 0
                each_account_awsloginrole_count = 0
                each_account_roles_to_be_deleted_count = 0

                report = []
                results_json = []
                each_account_roles_tobedeleted = []
                print('Starting for account ************************** : ' + account )
                # report.append('\n*******************************************************************************')
                # report.append('\nUnused roles report for account: \"' + account + '\"')
                # report.append('\n*******************************************************************************')
                # logging.info('*******************************************************************************')
                # logging.info('Unused roles report for account: \"' + account + '\"')
                # logging.info('*******************************************************************************')

                logger.info('Before assume Role')
                credentials = []
                try:
                    assume_role_object = sts_client.assume_role(
                        RoleArn='arn:aws:iam::'+str(account_id)+':role/service_security_lambda@awsevents_role',
                        RoleSessionName='AssumeGetCredRole',
                        ExternalId='zulu0-'+account,
                        DurationSeconds=3600)
                    logger.info('After assume Role')

                    credentials = assume_role_object['Credentials']
                except ClientError as e:
                    logger.error("Below error1 occured assuming role for account : " + account)
                    logger.exception(e)
                    continue
                except Exception as e:
                    logger.error("Below error2 occured assuming role for account : " + account)
                    logger.exception(e)
                    continue



                iam = boto3.client('iam',
                                   aws_access_key_id=credentials['AccessKeyId'],
                                   aws_secret_access_key=credentials['SecretAccessKey'],
                                   aws_session_token=credentials['SessionToken'])

                iam_res = boto3.resource('iam',
                                   aws_access_key_id=credentials['AccessKeyId'],
                                   aws_secret_access_key=credentials['SecretAccessKey'],
                                   aws_session_token=credentials['SessionToken'])

                logger.info("Before list roles")
                all_account_roles = iam.list_roles(MaxItems=1000)
                logger.info("NUMBER OF ROLES FOUND IN ACCOUNT: " + str(len(all_account_roles['Roles'])))
                logger.info("NUMBER OF ROLES FOUND IN ACCOUNT: " + str(len(all_account_roles['Roles'])))
                # report.append("\nNUMBER OF ROLES FOUND IN ACCOUNT: " + str(len(all_account_roles['Roles'])))
                # report.append("\nFIND BELOW ROLES WHICH ARE NEVER USED : " )

                for role in all_account_roles['Roles']:
                    print('each role for loop')
                    logger.info(
                        "\n************************************************************************************************************************")
                    logger.info("Checking for policies in Role : " + role['RoleName'])
                    role_details = iam.get_role(RoleName=role['RoleName'])
                    if ((not (role_details['Role']['RoleLastUsed']) and (datetime.now(timezone.utc)-role_details['Role']['CreateDate']).days <= 180)):
                        logger.info("Role never used since creation, but created in recent times : " + role['RoleName'])
                    elif role_details['Role']['RoleLastUsed'] and role_details['Role']['RoleLastUsed']['LastUsedDate'] and (datetime.now(timezone.utc)-role_details['Role']['RoleLastUsed']['LastUsedDate']).days <= 180:
                        logger.info("Role used in recent times, 180 days : " + role['RoleName'])
                    else:
                        each_account_count = each_account_count + 1
                        report.append({'role': role['RoleName'], 'account_name' : account , 'account_id':account_id})
                        # report.append('\n      ' + role['RoleName'])
                        if 'awslogin@' in role['RoleName'] or 'AWSServiceRole' in role['RoleName']:
                            each_account_awsloginrole_count = each_account_awsloginrole_count + 1
                        else:
                            # print('reached else, deletion roles')
                            each_account_roles_tobedeleted.append({'role': role['RoleName'], 'account_name' : account , 'account_id':account_id})
                            results_json.append({'user':role['RoleName'],'account':each_account['account_name'],'voilation':'aws_iam_ununsed_roles'})
                            # each_account_roles_tobedeleted[account+'-'+account_id].append(role['RoleName'])
                            # each_account_roles_to_be_deleted_count = each_account_roles_to_be_deleted_count + 1

                    # summary_report.append('\n' + account + ' :: total_unused_roles : ' + str(
                    #     each_account_count) + ', awslogin_roles : ' + str(each_account_awsloginrole_count) + ', roles_tobe_deleted :' + str(each_account_roles_to_be_deleted_count))

                logger.info('\n' + account + ' :: total_unused_roles : ' + str(
                    each_account_count) + ', awslogin_roles : ' + str(each_account_awsloginrole_count) + ', roles_tobe_deleted :' + str(each_account_roles_to_be_deleted_count))
                logger.info(report)


                if each_account_roles_tobedeleted:
                    csv_columns = ['role', 'account_name', 'account_id']
                    with open('/tmp/unused_roles/'+account+'_unused_roles.csv', 'w') as of:
                        writer = csv.DictWriter(of, fieldnames=csv_columns)
                        writer.writeheader()
                        for data in each_account_roles_tobedeleted:
                            writer.writerow(data)

                    store_report_in_s3('/tmp/unused_roles/'+account+'_unused_roles.csv',notification_type, account)

                            # for line in report:
                            #     of.write(line)

                    logger.info('Ending for account ************************** : ' + account)
                f_rotation = io.StringIO("")
                if results_json:
                    logger.info("****************************Users needing access key rotation************************")
                    logger.info(results_json)
                    for each_unused_role in results_json:
                        json.dump(each_unused_role, f_rotation)
                        f_rotation.write('\n')
                    store_notification_in_s3(f_rotation.getvalue(),notification_type, account, now.year, now.month, now.day)
            refreshAthenaPartitions('awssec_iam_voilation_data')

                # if each_account_roles_tobedeleted:
                #     print('Roles to be deleted ************')
                #     print(each_account_roles_tobedeleted)
                #     with open('unused_roles/' + dt_folder + '/accounts_to_be_deleted_report.json', 'w') as asf:
                #         asf.write(str(json.dumps(each_account_roles_tobedeleted)))

                # if summary_report:
                #     with open('unused_roles/' + dt_folder + '/summary_report.txt', 'w') as sf:
                #         for line in summary_report:
                #             sf.write(line)
