#!/usr/local/bin/bash
mgmt_account="<Master AWS Account ID>"
prefix="vpc-flow-logs"
declare -A buckets
# can override the default buckets...
#buckets["us-east-2"]="arn:aws:s3:::helix-flow-logs-920379730419-us-east-2/o-mzamfui7aq"

if [ -z "$3" ]; then
	echo "Usage: $0 [<account>] <region> <vpc-id> [<profile>]"
	echo "use a placeholder for account if profile is specified"
	exit 1
fi

acct="$1"
region="$2"
vpc="$3"
profile="$4"
user="$(id -u -n)"
if [ -z "$profile" ]; then
	profile="$user-$acct"
fi
scriptname="$(basename "$0")"
logname="log-archive-flow-logs-$vpc"

logbucket="${buckets[$region]}"
if [ -z "$logbucket" ]; then
	# This should work for most purposes
	logbucket="arn:aws:s3:::log-archive-flow-logs-${mgmt_account}-${region}/${prefix}"
fi

flowlogs="$(aws-vault exec "$profile" -- aws ec2 describe-flow-logs --region "$region" --filter "Name=resource-id,Values=${vpc}")"
if [ "$?" -ne 0 ]; then
	echo "Error getting flow logs for ${vpc} in ${region}"
	exit 1
fi
#echo $flowlogs | jq .

echo "Checking for existing flow log '${logname}' for ${vpc} in ${region}"
flowlogids="$(echo "$flowlogs" | jq -r ".FlowLogs[].FlowLogId")"
found=no
for id in $flowlogids; do
	echo -n "Checking $id... "
	name="$(echo "$flowlogs" | jq -r ".FlowLogs[] | select(.FlowLogId==\"$id\") | .Tags[] | select(.Key==\"Name\") | .Value" 2>/dev/null)"
	echo "$name"
	if [ "$name" == "$logname" ]; then
		found=yes
		mgr="$(echo "$flowlogs" | jq -r ".FlowLogs[] | select(.FlowLogId==\"$id\") | .Tags[] | select(.Key==\"fe_common.managed_by\") | .Value" 2>/dev/null)"
		echo "Found $name, managed by $mgr"
		break
	fi
done

if [ "$found" == "yes" ]; then
	echo "The flow log was found, no further action."
	exit 0
fi

echo "Not found.  Creating, target $logbucket ..."

# Tags
# Can also use: 	ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=$logname},{Key=fe_common.managed_by,Value=$scriptname},{Key=fe_common.cost_center,Value=com_infra-prod}]
read -r -d '' tags <<-END_TAGS
[
	{
		"ResourceType": "vpc-flow-log",
		"Tags": [
			{
				"Key": "Name",
				"Value": "$logname"
			},
			{
				"Key": "fe_common.managed_by",
				"Value": "$scriptname"
			},
			{
				"Key": "fe_common.cost_center",
				"Value": "com_infra-prod"
			},
			{
				"Key": "fe_common.env_type",
				"Value": "prod"
			},
			{
				"Key": "fe_common.owner_accountname",
				"Value": "cloud-infrastructure@fireeye.com"
			},
			{
				"Key": "fe_common.product",
				"Value": "infra"
			}

		]
	}
]
END_TAGS


aws-vault exec "$profile" -- aws ec2 create-flow-logs --region "$region" \
	--resource-type VPC \
	--resource-ids "${vpc}" \
	--traffic-type ALL \
	--log-destination-type s3 \
	--log-destination "$logbucket" \
	--max-aggregation-interval 60 \
	--tag-specification "${tags}"
