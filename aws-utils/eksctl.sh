#!/bin/bash

PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"

for PROF in ${PROFILES[@]}; do
    regions=$(aws ec2 describe-regions --profile ${PROF} --output json | jq -r '.Regions | .[].RegionName')
    echo $regions
    for r in $regions; do
        echo "Checking region: $r"  
        # List EKS clusters in current region
        clusters=$(aws eks list-clusters --region ${r} --profile ${PROF} --query 'clusters[]' --output text)    
        echo $clusters
        # If clusters exist in this region
        if [ ! -z "$clusters" ]; then
            echo "Found clusters in $r:"

            # Iterate through each cluster
            for cluster in $clusters; do
                echo "Adding cluster: $cluster"
                # eksctl utils write-kubeconfig --cluster ${cluster} --region ${r} --profile ${PROF} --auto-kubeconfig
                aws eks update-kubeconfig --region ${r} --name ${cluster} --profile ${PROF}
            done
        fi
    done
done
