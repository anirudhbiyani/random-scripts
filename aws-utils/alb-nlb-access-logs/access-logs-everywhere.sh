#!/usr/local/bin/bash
mgmt_account="<Master AWS Account ID>"
bucket_prefix="lb-access-logs"

PROFILES="$(grep 'profile' ~/.aws/config | awk {print substr($2, 1, length($2)-1)})"

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
	local elbarns
	local out
	local logbucket
	logbucket=
	raw="$(aws-vault exec "${1}" -- aws --region $2 elbv2 describe-load-balancers)"
	if [ "$?" -ne 0 ]; then
		echoerr "Could not get ELBs for $1 in $2"
		return 1
	fi
	out=""
	elbarns="$(echo "$raw" | jq -r ".LoadBalancers[].LoadBalancerArn")"
	local arn
	local rawattrs
	local logenabled
	for arn in $elbarns; do
	  type="$(echo "$arn" | awk -F: '{print $6}' | awk -F/ '{print $2}')"
	  #type="$(echo "$raw" | jq -r ".LoadBalancers[] | select(.LoadBalancerArn==\"$arn\") | .Type")"
    case "$type" in
    app)
      logbucket="log-archive-alb-logs-${mgmt_account}-${2}"
      ;;
    net)
      logbucket="log-archive-nlb-logs-${mgmt_account}-${2}"
      ;;
    *)
      echo "Unknown LB type: $type"
      continue
      ;;
    esac
		rawattrs="$(aws-vault exec "${1}" -- aws --region $2 elbv2 describe-load-balancer-attributes --load-balancer-arn "$arn")"
		logenabled="$(echo "$rawattrs" | jq -r ".Attributes[] | select(.Key==\"access_logs.s3.enabled\") | .Value" 2>/dev/null)"
		case $logenabled in
		true)
		  existingbucket="$(echo "$rawattrs" | jq -r ".Attributes[] | select(.Key==\"access_logs.s3.bucket\") | .Value" 2>/dev/null)"
		  existingprefix="$(echo "$rawattrs" | jq -r ".Attributes[] | select(.Key==\"access_logs.s3.prefix\") | .Value" 2>/dev/null)"
		  if [ "$existingbucket" == "$logbucket" ] && [ "$existingprefix" == "$bucket_prefix" ]; then
		    echo -n '★'
		  else
		    echo -n '▼'
		    cantelbs="$cantelbs\n$arn\t$existingbucket/$existingprefix"
		  fi
		  ;;
		false)
		  echo -n '✔'
		  #echo elbs["$arn"]="type"
		  elbs["$arn"]="$type"
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
			echo "ELB: ${elb} ${elbs[$elb]}"
			echo "$(date "+%s") $profile $region $elb" >> "apply-$$.log"
			./setup-access-log-alb-nlb.sh "nada" "$region" "$elb" "$profile"
		done
		if [ -n "$cantelbs" ]; then
		  echo "[$profile $region] Cannot set on these ELBs:" | tee -a "cannot-$$.log"
		  echo -e "$cantelbs" | column -t | tee -a "cannot-$$.log"
    fi
	done
done
