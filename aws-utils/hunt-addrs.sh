#!/bin/bash
# This script hunts for the given ec2 address across all accounts
if [ -z "$1" ]; then
	echo "supply IP"
	exit 1
fi
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES}; do
	echo "##### ${PROF} #####"
	aws-vault exec ${PROF} -- aws --region us-west-2 ec2 describe-addresses --public-ips $1
done
