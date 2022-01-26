#!/usr/bin/env bash

#PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
PROFILES=(delta0 delta1 delta2 delta3 delta4 delta5 delta6 delta7 delta8 delta9 delta10 delta11 delta12 delta13 delta14 delta15)
#PROFILES=(charlie0 charlie1 charlie3 charlie4 charlie5 charlie6 charlie7 charlie8 charlie9 charlie10 charlie11 charlie12 charlie13 charlie14 charlie15 charlie16 charlie17 charlie18)
#PROFILES=(hotel0 hotel1 iss0 iss1 csm0 sierra0 foxtrot0 foxtrot1 echo0 mike0 mike1 mandiant-legacy master quebec0 felabs0 fso0 cleancommunications oscar0)
#PROFILES=(mandiantredteam cloudvisory cloudvisory2 cloudvisory3 cloudvisory4 cloudvisory5)

for PROF in ${PROFILES[@]};
do
  regions=$(aws-vault exec ${PROF} -- aws ec2 describe-regions | jq -r '.Regions | .[].RegionName')
  for r in $regions;
  do
    echo "---------------------------------------------------------"
    echo "                       "$PROF - $r"                      "
    vpcid=$(aws-vault exec ${PROF} -- aws ec2 describe-vpcs --region $r | jq -r '.Vpcs | .[].VpcId')
    for i in ${vpcid[@]};
    do
      # This is to check if the VPC is empty or not by checking if there are any ENI present in it.
      count=$(aws-vault exec ${PROF} -- aws ec2 describe-network-interfaces --filters Name=vpc-id,Values=$i --region $r | jq '.NetworkInterfaces | length')
      if [[ $count -eq 0 ]]; then
        echo "Unused VPC - "$i
        ig=$(aws-vault exec ${PROF} -- aws ec2 describe-internet-gateways --filters Name=attachment.vpc-id,Values=$i --region $r | jq -r '.InternetGateways | .[].InternetGatewayId')
        for x in ${ig[@]}; do
          aws-vault exec ${PROF} -- aws ec2 detach-internet-gateway --internet-gateway-id $x --vpc-id $i --region $r
          aws-vault exec ${PROF} -- aws ec2 delete-internet-gateway --internet-gateway-id $x --region $r
        done

        subnet=$(aws-vault exec ${PROF} -- aws ec2 describe-subnets --filters Name=vpc-id,Values=$i --region $r | jq -r '.Subnets | .[].SubnetId')
        for x in ${subnet[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-subnet --subnet-id $x --region $r
        done

        rt=$(aws-vault exec ${PROF} -- aws ec2 describe-route-tables --filters Name=vpc-id,Values=$i --region $r | jq -r '.RouteTables | .[].RouteTableId')
        for x in ${rt[@]}; do
          assoc=$(aws-vault exec ${PROF} -- aws ec2 describe-route-tables --route-table $rt --region $r | jq -r '.RouteTables | .[].Associations | .[].RouteTableAssociationId')
          for y in ${assoc[@]}; do
            aws-vault exec ${PROF} -- aws ec2 disassociate-route-table --association-id $y --region $r
          done
          aws-vault exec ${PROF} -- aws ec2 delete-route-table --route-table-id $x --region $r
        done

        nacl=$(aws-vault exec ${PROF} -- aws ec2 describe-network-acls --filters Name=vpc-id,Values=$i --region $r | jq -r '.NetworkAcls | .[].NetworkAclId')
        for x in ${nacl[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-network-acl --network-acl-id $x --region $r
        done

        peer=$(aws-vault exec ${PROF} -- aws ec2 describe-vpc-peering-connections --filters Name=requester-vpc-info.vpc-id,Values=$i --region $r | jq -r '.VpcPeeringConnections | .[].VpcPeeringConnectionId')
        for x in ${peer[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-vpc-peering-connection --vpc-peering-connection-id $x --region $r
        done

        endpt=$(aws-vault exec ${PROF} -- aws ec2 describe-vpc-endpoints --filters Name=vpc-id,Values=$i --region $r | jq -r '.VpcEndpoints | .[].VpcEndpointId')
        for x in ${endpt[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-vpc-endpoints --vpc-endpoint-ids $x --region $r
        done

        nat=$(aws-vault exec ${PROF} -- aws ec2 describe-nat-gateways --filter Name=vpc-id,Values=$i --region $r | jq -r '.NatGateways | .[].NatGatewayId')
        for x in ${nat[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-nat-gateway --nat-gateway-id $x --region $r
        done

        sg=$(aws-vault exec ${PROF} -- aws ec2 describe-security-groups --filters Name=vpc-id,Values=$i --region $r | jq -r '.SecurityGroups | .[].GroupId')
        for x in ${sg[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-security-group --group-id $x --region $r
        done

        vpn=$(aws-vault exec ${PROF} -- aws ec2 describe-vpn-gateways --filters Name=attachment.vpc-id,Values=$i --region $r | jq -r '.VpnGateways | .[].VpnGatewayId')
        for x in ${vpn[@]}; do
          aws-vault exec ${PROF} -- aws ec2 delete-vpn-gateway --vpn-gateway-id $x --region $r
        done

        aws-vault exec ${PROF} -- aws ec2 delete-vpc --vpc-id $i --region $r
        if [ "$?" -eq 0 ]; then
          echo "VPC successfully Deleted"
        else
          echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
          echo "Could not delete VPC"
          echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        fi
      fi
      echo "---------------------------------------------------------"
   done
  done
done
