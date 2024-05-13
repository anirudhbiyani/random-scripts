#!/usr/bin/env bash

hostname="dreamplug.okta.com"

# Check if OKTA_TOKEN in environment variable is set or not
if [[ -z "${OKTA_TOKEN}" ]]; then
  echo "Define OKTA_TOKEN as environment variable before running the script. Exiting now."
  exit 1
fi

# Get memebers
mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/users")
users=$(jq -r '.[] | select(.status == "ACTIVE") | .id' <<< "$mem")

for r in ${users[@]};
do
  user=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/users/${r}")
  lastused=$(jq -r '.lastLogin' <<< $user)
  name=$(jq -r '.profile | [.firstName, .lastName]' <<< $user)
  # 2022-04-29T15:43:43.000Z
  d=$(sed 's/\(.*\).000Z/\1/' <<< $lastused)
  cdate=$(date -juf %Y-%m-%dT%H:%M:%S +%s $d)
  old=$(date -v -90d +%s)
  if [ $cdate -lt $old ]; then
    echo $(echo "${name[*]}" has not logged in last 90 days. Last login - $d)
  fi
done
