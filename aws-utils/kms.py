#!/usr/bin/env python

'''
Checks if a particular AWS KMS Key has key rotation enabled or not.
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20150312"

import boto
import datetime
import json
import time
from pprint import pprint
from boto.kms.layer1 import KMSConnection

def main():

    filename = 'kms-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f=open(filename,'a')
    f.write('Date Time | Key Name | Status' + '\n')
    conn = boto.kms.connect_to_region('us-west-1')
    for loop in range(1, conn.list_keys()['KeyCount']):
        key = conn.list_keys()['Keys'][loop]['KeyId']
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.list_keys()['Keys'][loop]['KeyId'] + '|'+ str(conn.get_key_rotation_status(key)['KeyRotationEnabled']) + '\n')
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_key(key)['KeyMetadata']['KeyId'] + '|' + conn.describe_key(key)['KeyMetadata']['KeyState'] + '\n')
        f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_key(key)['KeyMetadata']['KeyId'] + '|' + str(conn.list_grants(key)['GrantCount']) + '\n')
        result = conn.get_key_policy(key, 'default')['Policy']
        j = json.loads(result)
        for i in xrange(str(j).count('Action')):
                if not ('853268358782') in j['Statement'][i]['Principal']:
                    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_key(key)['KeyMetadata']['KeyId'] + '|' + 'True \n')
                else:
                    f.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + conn.describe_key(key)['KeyMetadata']['KeyId'] + '|' + 'False \n')

if __name__ == '__main__':
    main()
