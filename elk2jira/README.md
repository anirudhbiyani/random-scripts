# Alert Automation #

A simple script to send all the alerts generated via ELK to JIRA.

The script pulls all the alerts triggered from ELK in last 2 minutes and creates a case for each alert in TheHive platform, also `HIGH` and `CRITICAL` severity alerts are sent to slack at defined channel.

### Configuration ###
Add following details to `config.yaml`.

- Elasticsearch data-node/coordinating-nore url to the host list.
- Elasticsearch `api-id` and `api-key`.
- TheHive `url` and `apiKey`.
- Slack: `slack webhook` url and `channel` to which alerts will be sent.