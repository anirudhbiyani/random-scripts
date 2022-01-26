#!/bin/bash

checkUsername()
{
  # Check if username is not null
  if [[ -z "${username}" ]]; then
    echo "Username needed to continue. Exiting now."
    exit 1
  fi

  # Checking if the username ends with the following domains
  if [[ $domain != "fireeye.com" && $domain != "mandiant.com" ]]; then
    echo "Invalid username. The email address should either be a @fireeye.com or @mandiant.com address."
    exit 1
  fi

  # Check if the user exists
  response=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/users/${username}")
  userId=$(jq -r '.id' <<< "$response")

  if [[ -z "${userId}" ]]; then
    jq .errorSummary <<< "$response"
    exit 1
  fi
}
checkGroupname()
{
  # Check if group name is not null.
  if [[ -z "${group}" ]]; then
    echo "Group name needed to continue. Exiting now."
    exit 1
  fi

  # Check if the groupname start with aws-
  if [[ $groupname != "aws-" ]]; then
    echo "Invalid groupname. \"It should begin with aws- \"aws-<account-name>-<job-function>-<admin|nonadmin>"
    exit 1
  fi
}
searchGroupname()
{
  grpresponse=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}//api/v1/groups?q=${group}&limit=10")
  count=$(jq '. | length' <<< "$grpresponse")

  if [[ $count -gt 1 ]]; then
    echo "Multiple groups matched the input, cannot continue."
    exit 1
  fi

  if [[ $count -eq 0 ]]; then
    echo "No group found with this name, cannot continue."
    exit 1
  fi

  groupId=$(jq -r '.[].id' <<< "$grpresponse")
}
searchGroup()
{
  checkGroupname
  grpresponse=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}//api/v1/groups?q=${group}&limit=100")

  echo $(jq -r '.[].profile.name' <<< $grpresponse)

}
addUser()
{
  checkUsername
  checkGroupname
  searchGroupname
  echo "User Id for username ""$username"" is - ""$userId"
  echo "Group Id for groupname ""$group"" is - ""$groupId"
  echo "Operation being performed is - ""$action"
  curl -s -X PUT -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users/${userId}"

  mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users")
  result=$(jq -r '.[].id' <<< "$mem")

  if [[ "${result}" =~ ${userId} ]]; then
    echo "User ""$username"" was successfully added into group ""$group"
  fi

}
removeUser()
{
  checkUsername
  checkGroupname
  searchGroupname
  echo "User Id for username ""$username"" is - ""$userId"
  echo "Group Id for groupname ""$group"" is - ""$groupId"
  echo "Operation being performed is - ""$action"
  curl -X DELETE -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users/${userId}"

  mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users")
  result=$(jq -r '.[].id' <<< "$mem")

  if [[ ! "${result}" =~ ${groupId} ]]; then
    echo "User ""$username"" was successfully removed from the group ""$group"
  fi
}
createGroup()
{
  checkGroupname
  #           '{"profile": {"name": "West Coast Users","description": "All Users West of The Rockies"}}'
  groupjson='{"profile": {"name":"'"$group"'", "description":"This group has been created by '"$username"'"}}'
  mem=$(curl -s -X POST -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" -d "${groupjson}" "https://${hostname}/api/v1/groups")
  result=$(jq -r '.[].id' <<< "$mem" > /dev/null)

  if [[ -z "${result}" ]]; then
    jq .errorSummary <<< "$mem"
    exit 1
  fi

}
deleteGroup()
{
  checkUsername
  checkGroupname
  searchGroupname

  curl -s -X DELETE -H "Accept: application/json"-H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}"

  grpresponse=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}")
  result=$(jq .errorSummary <<< "$grpresponse")

  if [[ -n "${result}" ]]; then
    echo "The $group group has been successfully deleted."
  fi
}
listMembership()
{
  checkUsername
  echo "User Id for username ""$username"" is - ""$userId"
  echo "Operation being performed is - ""$action"
  mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/users/${userId}/groups")
  jq -r '.[].profile.name'  <<< "$mem"
}
listMembers()
{
  checkGroupname
  searchGroupname
  echo "Group Id for groupname ""$group"" is - ""$groupId"
  echo "Operation being performed is - ""$action"
  mem=$(curl -s -X GET -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: SSWS ${OKTA_TOKEN}" "https://${hostname}/api/v1/groups/${groupId}/users")
  jq -r '.[] | select(.status != "DEPROVISIONED") | .profile | [.displayName, .email, .department] | @tsv' <<< "$mem" | column -ts $'\t'
}
showUsage()
{
    echo "Usage: $0 [options [parameters]]"
    echo ""
    echo "Options:"
    echo " -u|--username, Enter the username on whih you want to perform the mentioned action"
    echo " -g|--group, Enter the group that you want to add the user to"
    echo " -a|--action, Enter the action that you want to perform - add, delete, createGroup, deleteGroup, searchGroup, list and listMembers"
    echo " -h|--help, Print help"

    return 0
}

# Taking the input parameter.
while [ -n "$1" ]; do
  case "$1" in
     --username|-u)
         shift
         echo "You entered username as - $1"
         username=$1
         ;;
     --group|-g)
         shift
         echo "You entered group as - $1"
         group=$1
         ;;
     --action|-a)
        shift
        echo "You entered action as - $1"
        action=$1
         ;;
     *)
        showUsage
        exit
        ;;
  esac
shift
done

domain=$(sed 's/.*@//' <<< "$username")
groupname=$(awk '{print substr($0,0,4)}' <<< "$group")
userId=""
groupId=""
hostname="fireeye.okta.com"

# Check if OKTA_TOKEN in environment variable is set or not
if [[ -z "${OKTA_TOKEN}" ]]; then
  echo "Define OKTA_TOKEN as environment variable before running the script. Exiting now."
  exit 1
fi

case $action in
  add)
    addUser
    ;;
  remove)
    removeUser
    ;;
  createGroup)
    createGroup
    ;;
  deleteGroup)
    deleteGroup
    ;;
  searchGroup)
    searchGroup
    ;;
  list)
    listMembership
    ;;
  listMembers)
    listMembers
    ;;
  *)
    showUsage
    exit
    ;;
esac
