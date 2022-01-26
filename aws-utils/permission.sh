#!/bin/bash
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES}; do
    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    r=$(aws-vault exec ${PROF} -- aws iam list-policies --scope All --only-attached  --output json | jq -r '.Policies | .[].Arn')
    for i in $r; do
        out=$(aws-vault exec ${PROF} --  aws iam get-policy --policy-arn $i)
        version=$(aws-vault exec ${PROF} -- aws iam get-policy --policy-arn $i | jq -r '.Policy.DefaultVersionId')
        document=$(aws-vault exec ${PROF} -- aws iam get-policy-version --policy-arn $i --version-id $version)
        resource=$(jq -r 'select(.PolicyVersion.Document.Statement | .[].Resource == "*")' <<< $document)
        action=$(jq -r 'select(.PolicyVersion.Document.Statement | .[].Action == "*")' <<< $document)
        if [ ! -z "${action}"  ] ; then
            if [ ! -z "${resource}" ]; then
              echo $i
              echo "This policy is attached at -" $(aws-vault exec ${PROF} -- aws iam list-entities-for-policy --policy-arn $i)
            fi
        fi
    done
done
