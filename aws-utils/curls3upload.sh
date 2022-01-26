#!/bin/bash

# title           - curls3upload.sh
# description     - Uploads a user specified file into user specified bucket.
# author					- Aniruddha Biyani
# date            - 20170107
# version         - v1
# usage		 				- bash curls3upload.sh
# Note            - You might need to change the AWS Endpoint based on where your bucket is hosted.

file="$1"
bucket="$2"

key_id="XXXXXXXXXXXX"
key_secret="YYYYYYYYYYYYYYYYYY"

path="$file"
content_type="application/octet-stream"
date="$(LC_ALL=C date -u +"%a, %d %b %Y %X %z")"
md5="$(openssl md5 -binary < "$file" | base64)"

sig="$(printf "PUT\n$md5\n$content_type\n$date\n/$bucket/$path" | openssl sha1 -binary -hmac "$key_secret" | base64)"

curl -T $file http://$bucket.s3-ap-southeast-2.amazonaws.com/$path \
    -H "Date: $date" \
    -H "Authorization: AWS $key_id:$sig" \
    -H "Content-Type: $content_type" \
    -H "Content-MD5: $md5"
