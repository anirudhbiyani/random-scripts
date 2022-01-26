#!/bin/bash

#PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
PROFILES=(pci stage prod)
for PROF in "${PROFILES[@]}"; do
    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    listUsers=$(aws-okta exec ${PROF} -- aws iam list-users | jq -r '.Users | .[].UserName')
    for r in $listUsers; do
	     listKeys=$(aws-okta exec ${PROF} --  aws iam list-access-keys --user-name $r | jq -r '.AccessKeyMetadata | .[] | select(.Status=="Active") |.CreateDate')
       # aws-okta exec pci --  aws iam list-access-keys --user-name bitbucket| jq -r '.AccessKeyMetadata | select(.[].Status=="Active") | .[].CreateDate'
	     for i in $listKeys; do
		       LastUsedDate=$(sed 's/\(.*\):/\1/' <<< $i)
		       dtSec=$(date -j -f '%Y-%m-%dT%H:%M:%S%z' +'%s' $LastUsedDate)
		       taSec=$(date -v -365d +%s)
		       if [ $dtSec -lt $taSec ]; then
			          echo "Key Older than 360 days $r"
	         fi
	     done
    done
done
