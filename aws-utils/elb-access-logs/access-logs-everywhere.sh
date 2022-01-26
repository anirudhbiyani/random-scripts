#!/usr/local/bin/bash
mgmt_account="<Master AWS Account ID>"
bucket_prefix="elb-access-logs"

PROFILES="$(whoami)-india0 $(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"

# For testing
#PROFILES="$(whoami)-india0"
#PROFILES="india-ops-admin-delta4"

#user="$(id -u -n)"

declare -A elbs
cantelbs=""

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

# fetch ELB data data
# get_elbs(profile, region)
# sets elbs[]
function get_elbs {
	local raw
	local elbnames
	local out
	local logbucket
	logbucket="log-archive-elb-logs-${mgmt_account}-${2}"
	raw="$(aws-vault exec "${1}" -- aws --region $2 elb describe-load-balancers)"
	if [ "$?" -ne 0 ]; then
		echoerr "Could not get ELBs for $1 in $2"
		return 1
	fi
	out=""
	elbnames="$(echo "$raw" | jq -r ".LoadBalancerDescriptions[].LoadBalancerName")"
	local name
	local rawattrs
	local logenabled
	for name in $elbnames; do
		rawattrs="$(aws-vault exec "${1}" -- aws --region $2 elb describe-load-balancer-attributes --load-balancer-name "$name")"
		logenabled="$(echo "$rawattrs" | jq -r ".LoadBalancerAttributes.AccessLog.Enabled" 2>/dev/null)"
		case $logenabled in
		true)
		  existingbucket="$(echo "$rawattrs" | jq -r ".LoadBalancerAttributes.AccessLog.S3BucketName" 2>/dev/null)"
		  existingprefix="$(echo "$rawattrs" | jq -r ".LoadBalancerAttributes.AccessLog.S3BucketPrefix" 2>/dev/null)"
		  if [ "$existingbucket" == "$logbucket" ] && [ "$existingprefix" == "$bucket_prefix" ]; then
		    echo -n '★'
		  else
		    echo -n '▼'
		    cantelbs="$cantelbs\n$2/$name\t$existingbucket/$existingprefix"
		  fi
		  ;;
		false)
		  echo -n '✔'
		  #echo elbs["$name"]="$name"
		  elbs["$name"]="$name" # should use value for something
		  ;;
		*)
		  echo -n '✘'
		  ;;
    esac
	done
	echo
}

#set -x


echo '★ = already set correctly'
echo '▼ = already set to something else' "(see cannot-$$.log)"
echo '✔ = will apply'
echo '✘ = not supported by lb type'
echo "PID is $$"

for profile in $PROFILES; do
	echo "##### $profile #####"
	regions="$(get_regions $profile)"
	for region in $regions; do
		echo "Region: ${region}"
		elbs=()
		cantelbs=""
		get_elbs "$profile" "$region"
		for elb in "${!elbs[@]}"; do
			echo "ELB: ${elb}"
			echo "$(date "+%s") $profile $region $elb" >> "apply-$$.log"
			./setup-access-log-elb.sh "nada" "$region" "$elb" "$profile"
		done
		if [ -n "$cantelbs" ]; then
		  echo "[$profile $region] Cannot set on these ELBs:" | tee -a "cannot-$$.log"
		  echo -e "$cantelbs" | column -t | tee -a "cannot-$$.log"
    fi
	done
done
