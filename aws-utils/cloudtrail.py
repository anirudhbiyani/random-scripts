#!/usr/bin/env python

'''
Checks if a particular trail in CloudTrail is Encrypted on not.
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "hi@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20150312"

import boto
import datetime
import time
from boto.cloudtrail.layer1 import CloudTrailConnection

def main():

    filename = 'cloudtrail-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f=open(filename,'a')
    f.write('Date Time | Trail Name | Encryption Status' + '\n')
    conn = boto.cloudtrail.connect_to_region('us-east-1')
    k = ['Default']
    if conn.describe_trails(k)['trailList'][0]['KmsKeyId']:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_trails(k)['trailList'][0]['Name'] + '| True' + '| \n')
    else:
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_trails(k)['trailList'][0]['Name'] + '| False' + '| \n')

if __name__ == '__main__':
    main()
