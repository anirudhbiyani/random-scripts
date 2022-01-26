#!/bin/bash
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES}; do
    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    r=$(aws-vault exec ${PROF} -- aws iam list-roles --output json | jq .Roles | jq -r '.[].RoleName')
    for i in $r; do
        out=$(aws-vault exec ${PROF} -- aws iam list-role-policies --role-name $i --output json)
        echo $i"             "$(jq -e '.PolicyNames[]' <<< $out)
    done
done
