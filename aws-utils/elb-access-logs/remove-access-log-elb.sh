#!/usr/local/bin/bash
mgmt_account="<Master AWS Account ID>"
bucket_prefix="elb-access-logs"

if [ -z "$3" ]; then
	echo "Usage: $0 [<account>] <region> <elb-name> [<profile>]"
	echo "use a placeholder for account if profile is specified"
	exit 1
fi

acct="$1"
region="$2"
elb="$3"
profile="$4"
user="$(id -u -n)"
if [ -z "$profile" ]; then
	profile="$user-$acct"
fi
scriptname="$(basename $0)"

logbucket="log-archive-elb-logs-${mgmt_account}-${region}"

elbattrs="$(aws-vault exec "$profile" -- aws elb describe-load-balancer-attributes --region "$region" --load-balancer-name "$elb")"
if [ "$?" -ne 0 ]; then
	echo "Error getting attributes for ${elb} in ${region}"
	exit 1
fi
#echo $elbattrs | jq .
#exit
echo "Checking for access log config for ${elb} in ${region}"
logenabled="$(echo "$elbattrs" | jq -r ".LoadBalancerAttributes.AccessLog.Enabled" 2>/dev/null)"
#echo $logenabed
case $logenabled in
"true")
  echo "Access log enabled, disabling..."
  aws-vault exec "$profile" -- aws elb modify-load-balancer-attributes --region "$region" \
    --load-balancer-name "$elb" \
    --load-balancer-attributes \
      "{\"AccessLog\": {\"Enabled\": false}}"
  ;;
"false")
  echo "Access log already disabled."
  ;;
*)
  echo ".LoadBalancerAttributes.AccessLog.Enabled not supported on this ELB"
  ;;
esac
