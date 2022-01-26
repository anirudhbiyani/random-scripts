#!/usr/bin/env python3
import json
import requests
import ipaddress
import sys

aws_ip_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

try:
    ip = sys.argv[1]
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <ip address to check>")

try:
    ip_ranges = requests.get(aws_ip_url, timeout=30).json()['prefixes']
except requests.exceptions.HTTPError as errh:
    raise SystemExit(errh)
except requests.exceptions.ConnectionError as errc:
    raise SystemExit(errc)
except requests.exceptions.Timeout as errt:
    raise SystemExit(errt)
except requests.exceptions.RequestException as err:
    raise SystemExit(err)


for net in ip_ranges:
    if ipaddress.IPv4Interface(ip) in ipaddress.IPv4Network(net["ip_prefix"]):
        print(json.dumps(net, indent=1))
