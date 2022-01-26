#!/usr/bin/env bash

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES[@]};
do
    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    roles=$(aws-vault exec ${PROF} -- aws iam list-roles | jq -r '.Roles | .[].RoleName' | grep -v AWS | grep -v awslogin@)
    for r in ${roles[@]};
    do
      echo "Checking Role - "$r
      lastused=$(aws-vault exec ${PROF} -- aws iam get-role --role-name "$r" | jq -r '.Role.RoleLastUsed')
      if [[ "$lastused" == "{}" ]]; then
        datetime=$(aws-vault exec ${PROF} -- aws iam get-role --role-name "$r" | jq -r '.Role.CreateDate')
        d=$(sed 's/\(.*\)+00:00/\1/' <<< $datetime)
        cdate=$(date -juf %Y-%m-%dT%H:%M:%S +%s $d)
        old=$(date -v -14d +%s)
        if [ $cdate -lt $old ]; then
                  echo "Deleting $r from ${PROF}"

                  # Instance Profiles
                  echo "Removing Instance Profiles"
                  ip=$(aws-vault exec "${PROF}" -- aws iam list-instance-profiles-for-role --role-name "$r" | jq -r '.InstanceProfiles | .[].InstanceProfileName')
                  for a in $ip; do
                    echo "Removing Role from Instance Profile - $a"
                    aws-vault exec "${PROF}" -- aws iam remove-role-from-instance-profile --role-name "$r" --instance-profile-name "$a"
                  done

                  # Managed Policies
                  echo "Dettaching Managed Policies"
                  mp=$(aws-vault exec "${PROF}" -- aws iam list-attached-role-policies --role-name "$r" | jq -r '.AttachedPolicies | .[].PolicyArn')
                  for b in $mp; do
                    echo "Detaching Managed Policy - $b"
                    aws-vault exec "${PROF}" -- aws iam detach-role-policy --role-name "$r" --policy-arn "$b"
                  done

                  # Inline Policies
                  echo "Deleting Inline Policies"
                  ipl=$(aws-vault exec "${PROF}" -- aws iam list-role-policies --role-name "$r" | jq -r '.PolicyNames | .[]')
                  for c in $ipl; do
                    echo "Deleting Inline Policy - $c"
                    aws-vault exec "${PROF}" -- aws iam delete-role-policy --role-name "$r" --policy-name "$c"
                  done

                  echo "Removing $r from ${PROF}"
                  aws-vault exec "${PROF}" -- aws iam delete-role --role-name "$r"
                  if [ "$?" -eq 0 ]; then
                    echo "Role $r from ${PROF} deleted successfully."
                  else
                    echo "Role $r from ${PROF} could not be deleted."
                  fi
        echo "-------------------------------------------------------------------------------------------------------"
      fi
    fi
    done
done
