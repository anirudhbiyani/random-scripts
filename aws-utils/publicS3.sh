#!/usr/bin/env bash
while IFS=, read -r account bucket
do
  echo $account
  echo $bucket
  aws-vault exec $account -- aws s3api put-public-access-block --bucket $bucket --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
done < "$1"
