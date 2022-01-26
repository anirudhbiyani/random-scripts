#!/usr/local/bin/bash
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"

declare -A vpcs

echoerr() { echo "$@" 1>&2; }


# get_regions(profile)
function get_regions {
	aws-vault exec "${1}" -- aws ec2 describe-regions --no-all-regions | jq -r ".Regions[].RegionName"
	if [ "$?" -ne 0 ]; then
		echoerr "Could not get regions for $1"
		return 1
	fi
}

# return only us-west-2, for testing
function get_regions_x {
	echo "us-west-2"
}

# fetch VPC data
# get_vpcs(profile, region)
# sets vpcs[]
function get_vpcs {
	local raw
	local vpcids
	local out
	raw="$(aws-vault exec "${1}" -- aws --region $2 ec2 describe-vpcs)"
	if [ "$?" -ne 0 ]; then
		echoerr "Could not get VPCs for $1 in $2"
		return 1
	fi
	out=""
	vpcids="$(echo $raw | jq -r ".Vpcs[].VpcId")"
	local name
	for id in $vpcids; do
		name="$(echo $raw | jq -r ".Vpcs[] | select(.VpcId==\"$id\") | .Tags[] | select(.Key==\"Name\") | .Value" 2>/dev/null)"
		#echo $id $name 1>&2
		vpcs["$id"]="$name"
	done
}

#set -x

for profile in $PROFILES; do
	echo "##### $profile #####"
	regions="$(get_regions $profile)"
	for region in $regions; do
		echo "Region: ${region}"
		vpcs=()
		get_vpcs "$profile" "$region"
		for vpc in ${!vpcs[@]}; do
			echo "VPC: ${vpc} (${vpcs[$vpc]})"
			./remove-flow-logs-vpc.sh "nada" "$region" "$vpc" "$profile"
		done
	done
done
