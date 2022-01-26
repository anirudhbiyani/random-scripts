#!/bin/bash

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
echo $PROFILES
echo ""

for PROF in ${PROFILES}; do
  echo "##### ${PROF} #####"
  aws-vault exec ${PROF} -- aws iam get-account-authorization-details --output json  > ~/Desktop/${PROF}-iam-dump.json

  userList=$(jq '.UserDetailList | .[].UserName' ${PROF}-iam-dump.json)
  echo "These credentials that have access to ${PROF} account - "$userList

  groupList=$(jq '.GroupDetailList | .[].GroupName' ${PROF}-iam-dump.json)
  echo "These are groups that are present in ${PROF} account - "$groupList

  roleList=$(jq '.RoleDetailList | .[].GroupName' ${PROF}-iam-dump.json)
  echo "These are roles that are present in ${PROF} account - "$roleList
done
