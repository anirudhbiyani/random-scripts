#!/usr/local/bin/bash

if [ -z "$3" ]; then
	echo "Usage: $0 [<account>] <region> <eni-id> [<profile>]"
	echo "use a placeholder for account if profile is specified"
	exit 1
fi

acct="$1"
region="$2"
eni="$3"
profile="$4"
user="$(id -u -n)"
if [ -z "$profile" ]; then
	profile="$user-$acct"
fi
scriptname="$(basename $0)"
logname="elb-flow-log-$eni"

flowlogs="$(aws-vault exec "$profile" -- aws ec2 describe-flow-logs --region "$region" --filter "Name=resource-id,Values=${eni}")"
if [ "$?" -ne 0 ]; then
	echo "Error getting flow logs for ${eni} in ${region}"
	exit 1
fi
#echo $flowlogs | jq .

echo "Checking for existing flow log '${logname}' for ${eni} in ${region}"
flowlogids="$(echo $flowlogs | jq -r ".FlowLogs[].FlowLogId")"
found=no
remove_id=
for id in $flowlogids; do
	echo -n "Checking $id... "
	name="$(echo $flowlogs | jq -r ".FlowLogs[] | select(.FlowLogId==\"$id\") | .Tags[] | select(.Key==\"Name\") | .Value" 2>/dev/null)"
	echo "$name"
	if [ "$name" == "$logname" ]; then
		remove_id="$id"
		mgr="$(echo $flowlogs | jq -r ".FlowLogs[] | select(.FlowLogId==\"$id\") | .Tags[] | select(.Key==\"fe_common.managed_by\") | .Value" 2>/dev/null)"
		echo "Found $name, managed by $mgr"
		if [ "$mgr" == "setup-flow-logs-eni.sh" ]; then
		  found=yes
		  break
		fi
	fi
done

if [ "$found" == "no" ]; then
	echo "The flow log was not found, no further action."
	exit 0
fi

echo "Found it, removing $remove_id..."

aws-vault exec "$profile" -- aws ec2 delete-flow-logs --region "$region" \
	--flow-log-ids "$remove_id"

