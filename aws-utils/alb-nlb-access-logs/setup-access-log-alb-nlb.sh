#!/usr/local/bin/bash
mgmt_account="<Master AWS Account ID>"
bucket_prefix="lb-access-logs"

if [ -z "$3" ]; then
	echo "Usage: $0 [<account>] <region> <alb/nlb-arn> [<profile>]"
	echo "use a placeholder for account if profile is specified"
	exit 1
fi

acct="$1"
region="$2"
elb="$3"
profile="$4"
elbtype="$(echo "$elb" | awk -F: '{print $6}' | awk -F/ '{print $2}')"
user="$(id -u -n)"
if [ -z "$profile" ]; then
	profile="$user-$acct"
fi
scriptname="$(basename $0)"
logbucket=

case "$elbtype" in
app)
  logbucket="log-archive-alb-logs-${mgmt_account}-${region}"
  ;;
net)
  logbucket="log-archive-nlb-logs-${mgmt_account}-${region}"
  ;;
*)
  echo "Unknown LB type: $elbtype"
  exit 1
  ;;
esac

elbattrs="$(aws-vault exec "${profile}" -- aws --region $region elbv2 describe-load-balancer-attributes --load-balancer-arn "$elb")"
if [ "$?" -ne 0 ]; then
	echo "Error getting attributes for ${elb} in ${region}"
	exit 1
fi
#echo $elbattrs | jq .
#exit
echo "Checking for access log config for ${elb} in ${region}"
logenabled="$(echo "$elbattrs" | jq -r ".Attributes[] | select(.Key==\"access_logs.s3.enabled\") | .Value" 2>/dev/null)"
#echo $logenabed
case $logenabled in
"true")
  echo "Access log already enabled."
  ;;
"false")
  echo "Not enabled, setting it up..."
  aws-vault exec "$profile" -- aws elbv2 modify-load-balancer-attributes --region "$region" \
    --load-balancer-arn "$elb" \
    --attributes \
      "Key=access_logs.s3.enabled,Value=true" \
      "Key=access_logs.s3.bucket,Value=$logbucket" \
      "Key=access_logs.s3.prefix,Value=$bucket_prefix"
  ;;
*)
  echo ".LoadBalancerAttributes.AccessLog.Enabled not supported on this ELB"
  ;;
esac
