#!/bin/bash

# PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
PROFILES="india0"
echo $PROFILES
echo ""


for PROF in ${PROFILES}; do
  echo "##### ${PROF} #####"
  # aws-vault exec ${PROF} -- aws iam get-account-authorization-details --output json  > ${PROF}-iam-dump.json

  userCount=$(jq '.UserDetailList | length' ${PROF}-iam-dump.json)
  userCount=$(expr $userCount - 1)
  loop=$(seq 0 $userCount)
  for i in $loop; do
    userName=$(jq -r --arg i "$i" '.UserDetailList | .[$i | tonumber].UserName' ${PROF}-iam-dump.json)
    echo "${userName} is part of the following groups "$(jq -r --arg i "$i" '.UserDetailList | .[$i | tonumber].GroupList' ${PROF}-iam-dump.json)
    inlinePolicy=$(jq -r --arg i "$i" '.UserDetailList | .[$i | tonumber].UserPolicyList' ${PROF}-iam-dump.json)

    if [[ ! -z inlinePolicy]]; then
      echo "This user has inline policy. Dumped at "
    fi
  done
done

#  groupList=$(jq '.GroupDetailList | .[].GroupName' ${PROF}-iam-dump.json)
#  echo "These are groups that are present in ${PROF} account - "$groupList

#  roleList=$(jq '.RoleDetailList | .[].GroupName' ${PROF}-iam-dump.json)
#  echo "These are roles that are present in ${PROF} account - "$roleList
