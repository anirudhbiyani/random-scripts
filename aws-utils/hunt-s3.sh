#!/usr/bin/env bash

# This script hunts for the given ec2 address across all accounts
if [ -z "$1" ]; then
	echo "Name of the S3 Bucket"
	exit 1
fi

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"

for PROF in ${PROFILES}; do
	echo "##### ${PROF} #####"
	allbuckets=$(aws-vault exec "${PROF}" -- aws s3 ls  | cut -d" " -f3)
	echo $allbuckets

	if [[ "${allbuckets[@]}" =~  ${1} ]]; then
    echo "Found S3 Bucket in $PROF"
	fi
done
