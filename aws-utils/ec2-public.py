#!/usr/bin/env python

'''
This script outputs all EC2 instances in all regions with an Elastic IP Address attached to it.
'''

__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20170710"

import boto3, datetime, sys


def main():
    role = sys.argv[1]
    boto3.setup_default_session(profile_name=role, region_name='us-west-2')
    res = boto3.client('ec2')
    r = res.describe_instances().values()
    for j in r:
        print j[0]
#        print j[0]['PublicIpAddress']
    #    print j[0]['Tags'][0]['Value']

if __name__ == '__main__':
    main()
