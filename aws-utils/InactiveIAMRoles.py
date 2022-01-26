import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import datetime, json, os, re
import logging

max_days_for_last_used = 180

def main():
    roles_authorization_details = []

    iam_client = boto3.client('iam', profile=)

    roles_list = iam_client.get_account_authorization_details(Filter=['Role'])

    while True:
        roles_authorization_details += roles_list['RoleDetailList']
        if 'Marker' in roles_list:
            roles_list = iam_client.get_account_authorization_details(Filter=['Role'], MaxItems=100, Marker=roles_list['Marker'])
        else:
            break

    all_roles = roles_authorization_details

    for role in all_roles:
        logger.info(f"WHATISTHIS:{role}, LASTUSED:{role.get('RoleLastUsed')}")
        role_name = role['RoleName']
        role_path = role['Path']
        role_creation_date = role['CreateDate']
        role_age_in_days = (datetime.datetime.now() - role_creation_date.replace(tzinfo=None)).days

        if 'RoleLastUsed' in role:
            role_last_used = role.get('RoleLastUsed')
        else:
            role_last_used = {}
            role_last_used['LastUsedDate'] = role['CreateDate']

        if role_age_in_days <= max_days_for_last_used:
            compliance_result = COMPLIANT
            reason = f"Role age is {role_age_in_days} days"
            evaluations.append(
                build_evaluation(role_name, compliance_result, notification_creation_time, resource_type=DEFAULT_RESOURCE_TYPE, annotation=reason))
            logger.info(f"COMPLIANT: {role_name} - {role_age_in_days} is newer or equal to {max_days_for_last_used} days")
            continue


        last_used_date = role_last_used.get('LastUsedDate', None)
        used_region = role_last_used.get('Region', None)

        if not last_used_date:
            compliance_result = NON_COMPLIANT
            reason = "No record of usage"
            logger.info(f"NON_COMPLIANT: {role_name} has never been used")
            return build_evaluation(role_name, compliance_result, notification_creation_time, resource_type=DEFAULT_RESOURCE_TYPE, annotation=reason)


        days_unused = (datetime.datetime.now() - last_used_date.replace(tzinfo=None)).days

        if days_unused > max_age_in_days:
            compliance_result = NON_COMPLIANT
            reason = f"Was used {days_unused} days ago in {used_region}"
            logger.info(f"NON_COMPLIANT: {role_name} has not been used for {days_unused} days, last use in {used_region}")
            return build_evaluation(role_name, compliance_result, notification_creation_time, resource_type=DEFAULT_RESOURCE_TYPE, annotation=reason)

        compliance_result = COMPLIANT
        reason = f"Was used {days_unused} days ago in {used_region}"
        logger.info(f"COMPLIANT: {role_name} used {days_unused} days ago in {used_region}")
        return build_evaluation(role_name, compliance_result, notification_creation_time, resource_type=DEFAULT_RESOURCE_TYPE, annotation=reason)


if '__name__' == '__main__':
    main()
