#!/usr/bin/env bash

curl -s https://awspolicygen.s3.amazonaws.com/js/policies.js -o services.json

sed -i'.bck' 's/app.PolicyEditorConfig=//' services.json

jq -r '.serviceMap | keys[] as $k | "\($k),\(.[$k] | .StringPrefix)"' services.json > awsserviceprefix.csv

rm services.json
rm services.json.bck