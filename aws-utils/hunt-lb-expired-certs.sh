#!/bin/bash
# Search all accounts for expired ELB certificates in ACM
NOW="$(date '+%Y-%m-%dT%H:%M:%S%z')"
PROFILES="$(grep 'profile' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES}; do
	echo "##### ${PROF} #####"
	ELBS="$(aws-vault exec ${PROF} -- aws --region us-west-2 elb describe-load-balancers)"
	CERTS="$(echo $ELBS | jq -Mr '.LoadBalancerDescriptions[].ListenerDescriptions[].Listener.SSLCertificateId | select(. != null)' | sort | uniq)"
	for CERT in ${CERTS}; do
		echo "- ${CERT} -"
		INFO="$(aws-vault exec ${PROF} -- aws --region us-west-2 acm describe-certificate --certificate-arn ${CERT})"
		EXP="$(echo $INFO | jq -Mr '.Certificate.NotAfter')"
		if [[ "${EXP}" < "${NOW}" ]]; then
			echo "Expired! ${EXP}"
		fi
	done
done
