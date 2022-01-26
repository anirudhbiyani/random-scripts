#!/bin/bash
for c in $(openssl ciphers 'ALL:eNULL' | tr ':' ' '); do
	echo | openssl s_client -connect <URL or Domain Name>:<Port Number> -cipher $c -tls1_2 > /dev/null 2>&1 && echo -e "$c"
done
