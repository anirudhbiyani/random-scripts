#!/usr/bin/env bash

hostname="fireeye.okta.com"

echo "Use this script when you want to copy membersip of users from one Okta group to another."
echo "Usage - $0 <Name of the Old Group> <Name of the New Group>"
echo "-----------------------------------------------------------------------------------------"

oldgroup=$1
newgroup=$2

echo "Migrating users from $oldgroup group into $newgroup group"

# Get GroupId - new group
grpresponse=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}//api/v1/groups?q=${newgroup}&limit=10")
count=$(jq '. | length' <<< "$grpresponse")

if [[ $count -gt 1 ]]; then
  echo "Multiple groups matched the input, cannot continue."
  exit 1
fi

if [[ $count -eq 0 ]]; then
  echo "No group found with this name, cannot continue."
  exit 1
fi

newgroupId=$(jq -r '.[].id' <<< "$grpresponse")

# Get GroupId - old group
grpresponse=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}//api/v1/groups?q=${oldgroup}&limit=10")
count=$(jq '. | length' <<< "$grpresponse")

if [[ $count -gt 1 ]]; then
  echo "Multiple Old groups matched the input, cannot continue."
  exit 1
fi

if [[ $count -eq 0 ]]; then
  echo "No old group found with this name, cannot continue."
  exit 1
fi

groupId=$(jq -r '.[].id' <<< "$grpresponse")

# Get memebers
mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users")
users=$(jq -r '.[] | select(.status != "DEPROVISIONED") | .id' <<< "$mem")

for j in $users
do
    username=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/users/${j}" | jq -r '.profile.displayName')

    # Assign memebers to new group
    curl -s -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${newgroupId}/users/${j}"

    mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${newgroupId}/users")
    result=$(jq -r '.[].id' <<< "$mem")

    if [[ "${result}" =~ ${j} ]]; then
      echo "User "$username " was successfully added into group ""$newgroup"
    fi
done
