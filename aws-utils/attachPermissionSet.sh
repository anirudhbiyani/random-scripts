#!/usr/bin/env bash
roles=(admin power developer readonly)

showUsage()
{
  echo "Usage - $0 -p <Name of the AWS Profile that you want to use.>"
}

while [ -n $1 ]; do
  case "$1" in
     --profile|-p)
         shift
         PROFILE=$1
         ;;
     *)
        showUsage
        exit
        ;;
  esac
shift
done

sso=$(aws sso-admin list-instances --profile $PROFILE | jq -r '.Instances | .[].InstanceArn')
identitystoreId=$(aws sso-admin list-instances --profile $PROFILE | jq -r '.Instances | .[].IdentityStoreId')
accountList=$(aws organizations list-accounts --profile $PROFILE | jq -r '.Accounts | .[].Id')
permissionsetList=$(aws sso-admin list-permission-sets --instance-arn $sso --profile $PROFILE | jq -r '.PermissionSets | .[]')

for j in "${permissionsetList[@]}"; do
  permissionsetName=$(aws sso-admin describe-permission-set --profile $PROFILE --instance-arn $sso --permission-set-arn $j |  jq -r '.PermissionSet.Name')
  if [[ $permissionsetName == "developer-access" ]]; then
    devId=$j
  elif [[ $permissionsetName == "administator-access" ]]; then
    adminId=$j
  elif [[ $permissionsetName == "poweruser-access" ]]; then
    powerId=$j
  elif [[ $permissionsetName == "readonly-access" ]]; then
    readId=$j
  fi
done

for i in "${accountList[@]}"; do
  accountName=$(aws organizations describe-account --account-id $i --profile $PROFILE | jq -r '.Account.Name' | awk '{print tolower($0)}' | sed 's/ //g' )
  for r in "${roles[@]}"; do
          att=aws-$accountName-$r
          if [[ $r == 'admin' ]]; then
            permissionsetArn=$adminId
          elif [[ $r == 'power' ]]; then
            permissionsetArn=$powerId
          elif [[ $r == 'developer' ]]; then
            permissionsetArn=$devId
          elif [[ $r == 'readonly' ]]; then
            permissionsetArn=$readId
          fi

          groupId=$(aws identitystore list-groups --identity-store-id $identitystoreId --filters "AttributePath=DisplayName,AttributeValue=$att" --profile $PROFILE)
          if [ -z "$groupId" ]; then
            echo "Cannot find the group - "$att
            echo "Skipping...."
            continue
          fi
          aws sso-admin create-account-assignment --instance-arn $sso --target-id $i --target-type AWS_ACCOUNT --permission-set-arn $permissionsetArn --principal-type GROUP --principal-id $groupId --profile $PROFILE
          if [[ "$?" -eq 0 ]]; then
            echo "Assignment Successfully Created for $r in account $i"
          else
            echo "Assignment Errored out while assigning $r in account $i"
            continue
          fi
          aws sso-admin provision-permission-set --instance-arn $sso --target-id $i --target-type AWS_ACCOUNT --permission-set-arn $permissionsetArn --profile $PROFILE
          if [[ "$?" -eq 0 ]]; then
            echo "AWS SSO Assignment Deployed for $r in account $i"
          else
            echo "AWS SSO Assignment errored out for $r in account $i"
          fi
  done
  superadminId=$(aws identitystore list-groups --identity-store-id $identitystoreId --filters "AttributePath=DisplayName,AttributeValue=ControlTowerAdmins" --profile $PROFILE)
  aws sso-admin create-account-assignment --instance-arn $sso --target-id $i --target-type AWS_ACCOUNT --permission-set-arn $adminId --principal-type GROUP --principal-id $superadminId --profile $PROFILE
  if [[ "$?" -eq 0 ]]; then
    echo "Assignment Successfully Created for ControlTowerAdmins in account $i"
  else
    echo "Assignment Errored out while assigning ControlTowerAdmins in account $i"
    continue
  fi
  aws sso-admin provision-permission-set --instance-arn $sso --target-id $i --target-type AWS_ACCOUNT --permission-set-arn $adminId --profile $PROFILE
  if [[ "$?" -eq 0 ]]; then
    echo "AWS SSO Assignment Deployed for ControlTowerAdmins in account $i"
  else
    echo "AWS SSO Assignment errored out for ControlTowerAdmins in account $i"
  fi
done
