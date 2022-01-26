#!/usr/bin/env bash

while IFS=, read -r account role
do
    echo "Deleting $role from $account"

    # Instance Profiles
    echo "Removing Instance Profiles"
    ip=$(aws-vault exec "$account" -- aws iam list-instance-profiles-for-role --role-name "$role" | jq -r '.InstanceProfiles | .[].InstanceProfileName')
    for a in $ip; do
      echo "Removing Role from Instance Profile - $a"
      aws-vault exec "$account" -- aws iam remove-role-from-instance-profile --role-name "$role" --instance-profile-name "$a"
    done

    # Managed Policies
    echo "Dettaching Managed Policies"
    mp=$(aws-vault exec "$account" -- aws iam list-attached-role-policies --role-name "$role" | jq -r '.AttachedPolicies | .[].PolicyArn')
    for b in $mp; do
      echo "Detaching Managed Policy - $b"
      aws-vault exec "$account" -- aws iam detach-role-policy --role-name "$role" --policy-arn "$b"
    done

    # Inline Policies
    echo "Deleting Inline Policies"
    ipl=$(aws-vault exec "$account" -- aws iam list-role-policies --role-name "$role" | jq -r '.PolicyNames | .[]')
    for c in $ipl; do
      echo "Deleting Inline Policy - $c"
      aws-vault exec "$account" -- aws iam delete-role-policy --role-name "$role" --policy-name "$c"
    done

    echo "Removing $role from $account"
    aws-vault exec "$account" -- aws iam delete-role --role-name "$role"
    if [ "$?" -eq 0 ]; then
      echo "Role $role from $account deleted successfully."
    else
      echo "Role $role from $account could not be deleted."
    fi
    echo "-------------------------------------------------------------------------------------------------------"
    
done < "$1"
