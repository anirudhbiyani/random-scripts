#!/bin/bash
# Search all accounts for expired ACM certificates
NOW="$(date '+%Y-%m-%dT%H:%M:%S%z')"
PROFILES="$(grep 'profile india-ops-admin' ~/.aws/config | awk '{print substr($2, 1, length($2)-1)}')"
for PROF in ${PROFILES}; do
	echo "##### ${PROF} #####"
	CERTS="$(aws-vault exec ${PROF} -- aws --region us-west-2 acm list-certificates --certificate-statuses EXPIRED | jq -r -M '.CertificateSummaryList[].CertificateArn')"
	for CERT in ${CERTS}; do
		echo $CERT
		INFO="$(aws-vault exec ${PROF} -- aws --region us-west-2 acm describe-certificate --certificate-arn ${CERT})"
		USE="$(echo "${INFO}" | jq -r -M '.Certificate.InUseBy')"
		if [[ "${USE}" != '[]' ]]; then
			# We have to do this date comparision because --certificate-statuses EXPIRED
			# doesn't seem to do what it says...
			EXP="$(echo $INFO | jq -Mr '.Certificate.NotAfter')"
			if [[ "${EXP}" < "${NOW}" ]]; then
				echo "In-use and expired! ${EXP}"
				echo "Used by: ${USE}"
			fi
		fi
	done
done
