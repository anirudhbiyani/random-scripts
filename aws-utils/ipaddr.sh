#!/bin/bash
if [ -z "$1" ]; then
	echo "supply IP"
	exit 1
fi

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
regions=$(aws-vault exec india0 -- aws ec2 describe-regions | jq  -r '.Regions[].RegionName')
for PROF in ${PROFILES}; do
    echo "---------------------------------------------------------"
    echo "                          "$PROF"                        "
    for region in ${regions}; do
      aws-vault exec ${PROF} -- aws --region $region ec2 describe-addresses --public-ips $1
    done
done
