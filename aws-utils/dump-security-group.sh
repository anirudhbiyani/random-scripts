#!/usr/bin/env bash

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
#PROFILES=(E2E)
for PROF in ${PROFILES[@]}; do
    regions=$(aws ec2 describe-regions --profile ${PROF} --output json | jq -r '.Regions | .[].RegionName')
    for r in $regions; do
        listEC2=$(aws ec2 describe-instances --profile ${PROF} --region ${r} --output json)
        if [[ $(jq '.Reservations | length' <<< $listEC2) -gt 0 ]]; then
             # for i in $listEC2; do
            jq -c '.Reservations | .[].Instances | .[]' <<< $listEC2 | while read i; do
                if [[ "$(jq -r '.PublicIpAddress' <<< $i)" != "null" ]]; then
                    listSecurityGroups=$(jq -r '.SecurityGroups | .[].GroupId' <<< $i | sort -nr)
                    for sg in $listSecurityGroups; do
                        jq -c '.SecurityGroupRules[]' <<< $(aws ec2 describe-security-group-rules --profile $PROF --region $r --filters Name="group-id",Values="$sg" --output json) | while read s; do
                            echo $PROF, $r, $sg, $(jq -r '.Tags | from_entries | .Name' <<< $i), $(jq -r '[.InstanceId, .KeyName, .LaunchTime, .PrivateIpAddress, .PublicIpAddress, .State.Name] | @csv' <<< $i), $(jq -r 'select(.IsEgress==false) | [.CidrIpv4, .FromPort, .ToPort, .IpProtocol] | @csv' <<< $s)
                        done
                    done
                fi
            done
        fi
    done
done