#!/usr/bin/env python

'''
This script monitors the status of all tunnels for all VPNs for a single EC2 region and also send an email notification when the VPN is down.
'''

__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20170710"

import json, boto3, datetime, smtplib, sys
from urllib2 import Request
from urllib2 import urlopen

global server="smtp.gmail.com:587"
global fromaddr=""
global toaddr=""
global ccaddr=""
global username=""

def statuschecker():
    ec2 = boto3.client('ec2', region_name='us-west-1')
    vpns = ec2.describe_vpn_connections()['VpnConnections']
    for vpn in vpns:
        if vpn['State'] == "available":
            if vpn['VgwTelemetry'][0]['Status'] == "UP" or vpn['VgwTelemetry'][1]['Status'] == "UP":
#               message = "{} VPN ID: {}, State: {}, Tunnel0: {}, Tunnel1: {}".format(region['RegionName'], vpn['VpnConnectionId'], vpn['State'], vpn['VgwTelemetry'][0]['Status'], vpn['VgwTelemetry'][1]['Status'])
                if(vpn['VpnConnectionId'] == "") # SPX VPN Connection ID
                    cust = SPX
                elif(vpn['VpnConnectionId'] == "") # MersCorp VPN Connection ID
                    cust = MersCorp
                else
                    cust = "Invalid/Unknown Value in Customer Name."

                message = "Customer: {}, VPN ID: {}, State: {}, Tunnel0: {}, Tunnel1: {} {} {}".format(cust, vpn['VpnConnectionId'], vpn['State'], vpn['VgwTelemetry'][0]['Status'], vpn['VgwTelemetry'][1]['Status'], vpn['VgwTelemetry'][0]['LastStatusChange'], vpn['VgwTelemetry'][1]['LastStatusChange'])
                print message
                value = sendemail(fromaddr, toaddr, ccaddr, "AWS - Site-to-Site VPN Connection is down.", username, secret, server)
                if(value != none)
                    print value
                else
                    print "Email sent successfully."

def sendemail(from_addr, to_addr_list, cc_addr_list, subject, message, login, password, smtpserver):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems

def logger(text):
    continue

if __name__ == '__main__':
    statuschecker()
