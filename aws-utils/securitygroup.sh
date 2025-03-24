#!/bin/bash

PROFILES=(DEV)

for PROF in ${PROFILES[@]}; do
    regions=$(aws ec2 describe-regions --profile ${PROF} --output json | jq -r '.Regions | .[].RegionName')
    for r in $regions; do
        echo "${PROF} ----------- ${r}"
        sgID=$(aws ec2 describe-security-groups --query "SecurityGroups[?IpPermissions[?contains(IpRanges[*].CidrIp, '0.0.0.0/0')]].GroupId" --profile ${PROF} --region ${r} --output json | jq -r '.[]')
        for sg in $sgID; do
            echo "Security Group ID: ${sg}"
            aws ec2 describe-security-groups --group-ids ${sg} --profile ${PROF} --region ${r} --output json | jq -r '.SecurityGroups[].IpPermissions[] | [.FromPort, .ToPort, .IpProtocol, .IpRanges[].CidrIp] | @csv'
        done
    done
done

# Steampipe Query 

 select
  instance_id,
  sg ->> 'GroupName' as group_name,
  sg ->> 'GroupId' as group_id,
  aws_vpc_security_group_rule.type,
  aws_vpc_security_group_rule.ip_protocol,
  aws_vpc_security_group_rule.from_port,
  aws_vpc_security_group_rule.to_port,
  aws_vpc_security_group_rule.cidr_ipv4
from
  aws_ec2_instance,
  jsonb_array_elements(security_groups) as sg
  join aws_vpc_security_group_rule on 
    sg ->> 'GroupId' = aws_vpc_security_group_rule.group_id
where
aws_vpc_security_group_rule.type = 'ingress'
and aws_vpc_security_group_rule.cidr_ipv4 = '0.0.0.0/0'
and (
  (
    aws_vpc_security_group_rule.ip_protocol = '-1' -- all traffic
    and aws_vpc_security_group_rule.from_port is null
  )
  or (
    aws_vpc_security_group_rule.from_port <= 22
    and aws_vpc_security_group_rule.to_port >= 22
  )
  or (
    aws_vpc_security_group_rule.from_port <= 3389
    and aws_vpc_security_group_rule.to_port >= 3389
  )
);