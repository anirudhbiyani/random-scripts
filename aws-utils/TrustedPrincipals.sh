#!/usr/bin/env  bash
ACCOUNTS="<Account Name:Account ID,Account Name:Account ID,Account Name:Account ID,Account Name:Account ID,Account Name:Account ID>"

mkdir -p .trust_audit

## find tfadmin-role in aws config, parse only the account name
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 14, length($2)-14)}' | sort)"
for PROF in ${PROFILES}; do
    AUDIT_STORE=".trust_audit/${PROF}"
    mkdir -p ${AUDIT_STORE}
    rm -f ${AUDIT_STORE}/*

    echo "---------------------------------------------------------"
    echo "                           "$PROF"                       "
    allRoles=$(aws-vault exec ${PROF} -- aws iam list-roles)

    for r in $(echo $allRoles | jq -r '.Roles[].RoleName'); do
      unset cleanup known external
      trustPolicy=$(echo $allRoles | jq --arg role "$r" '.Roles[] | select(.RoleName == $role) | .AssumeRolePolicyDocument.Statement')
      trustedPrincipals=$(echo $trustPolicy | jq -r '.[].Principal | to_entries[] | select(.key=="AWS").value | if type == "array" then .[] else . end')
      for t in $trustedPrincipals; do
        # filter out old/invalid IAM users and roles for cleanup (i.e. AROASJEOVWWEP63YMDX52, AIDAISLXRRB6IB3TFRHXK)
        if egrep -q '^A[A-Z0-9]{20}' <<< "$t"; then
          cleanup+="\n$t"
        else
          acctId=$(echo $t | cut -d: -f5)
          # check if known/managed account
          if grep -q "$acctId" <<< "${ACCOUNTS}"; then
            known+="\n$t"
          else
            external+="\n$t"
            echo "$trustPolicy" > ${AUDIT_STORE}/trust_policy-$r
          fi
        fi
      done
      [[ ! -z $cleanup ]]  && echo -e "==== $r ====$cleanup"  >> ${AUDIT_STORE}/cleanup
      [[ ! -z $known ]]     && echo -e "==== $r ====$known"     | tee -a ${AUDIT_STORE}/known
      [[ ! -z $external ]] && echo -e "==== $r ====$external" | tee -a ${AUDIT_STORE}/external
    done
done
