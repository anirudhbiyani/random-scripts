#!/usr/local/bin/bash
PROFILES="$(whoami)-india0 $(grep 'profile india-ops-admin' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"

# For testing
#PROFILES="$(whoami)-india0"

#user="$(id -u -n)"

declare -A enis

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

# fetch ENI data
# get_enis(profile, region)
# sets enis[]
function get_enis {
	local raw
	local eniids
	local out
	raw="$(aws-vault exec "${1}" -- aws --region $2 ec2 describe-network-interfaces)"
	if [ "$?" -ne 0 ]; then
		echoerr "Could not get ENIs for $1 in $2"
		return 1
	fi
	out=""
	eniids="$(echo $raw | jq -r ".NetworkInterfaces[].NetworkInterfaceId")"
	local desc
	local type
	for id in $eniids; do
		desc="$(echo $raw | jq -r ".NetworkInterfaces[] | select(.NetworkInterfaceId==\"$id\") | .Description" 2>/dev/null)"
		type="$(echo $raw | jq -r ".NetworkInterfaces[] | select(.NetworkInterfaceId==\"$id\") | .InterfaceType" 2>/dev/null)"
		#echo $id $name 1>&2
		case $type in
    network_load_balancer)
      enis["$id"]="$desc"
      echo -n '✔'
      ;;
    *)
      echo -n '✘'
      ;;
		esac
	done
	echo
}

#set -x

for profile in $PROFILES; do
	echo "##### $profile #####"
	regions="$(get_regions $profile)"
	for region in $regions; do
		echo "Region: ${region}"
		enis=()
		get_enis "$profile" "$region"
		for eni in "${!enis[@]}"; do
			echo "ENI: ${eni} (${enis[$eni]})"
			./remove-flow-logs-eni.sh "nada" "$region" "$eni" "$profile"
		done
	done
done
