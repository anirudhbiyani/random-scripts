#!/usr/bin/env  bash
# PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
PROFILES=(delta11 delta15 charlie4 charlie6 charlie9 charlie15 oscar0 india0 zulu0 master)
for PROF in "${PROFILES[@]}"; do
    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    listRoles=$(aws-vault exec ${PROF} -- aws iam list-roles | jq -r '.Roles | .[].RoleName')

    for r in $listRoles; do
      datetime=$(aws-vault exec ${PROF} -- aws iam get-role --role-name "$r" | jq -r '.Role.RoleLastUsed.LastUsedDate')
      if [ $datetime == "null" ]; then
        dtSec=$(date -r 0 +%s)
      else
        LastUsedDate=$(sed 's/\(.*\):/\1/' <<< $datetime)
        dtSec=$(date -j -f '%Y-%m-%dT%H:%M:%S%z' +'%s' $LastUsedDate)
      fi
      taSec=$(date -v -180d +%s)
      if [ $dtSec -lt $taSec ]; then
            echo "Deleting $r from $PROF"

            # Instance Profiles
            echo "Removing Instance Profiles"
            ip=$(aws-vault exec "$PROF" -- aws iam list-instance-profiles-for-role --role-name "$r" | jq -r '.InstanceProfiles | .[].Roles | .[].RoleName')
            for a in $ip; do
              echo "Removing Role from Instance Profile - $a"
              aws-vault exec "$PROF" -- aws iam remove-role-from-instance-profile --role-name "$r" --instance-profile-name "$a"
            done

            # Managed Policies
            echo "Dettaching Managed Policies"
            mp=$(aws-vault exec "$PROF" -- aws iam list-attached-role-policies --role-name "$r" | jq -r '.AttachedPolicies | .[].PolicyArn')
            for b in $mp; do
              echo "Detaching Managed Policy - $b"
              aws-vault exec "$PROF" -- aws iam detach-role-policy --role-name "$r" --policy-arn "$b"
            done

            # Inline Policies
            echo "Deleting Inline Policies"
            ipl=$(aws-vault exec "$PROF" -- aws iam list-role-policies --role-name "$r" | jq -r '.PolicyNames | .[]')
            for c in $ipl; do
              echo "Deleting Inline Policy - $c"
              aws-vault exec "$PROF" -- aws iam delete-role-policy --role-name "$r" --policy-name "$c"
            done

            echo "Removing $r from $PROF"
            aws-vault exec "$PROF" -- aws iam delete-role --role-name "$r"
            if [ "$?" -eq 0 ]; then
              echo "Role $r from $PROF deleted successfully."
            else
              echo "Role $r from $PROF could not be deleted."
            fi
      fi
    done
done
