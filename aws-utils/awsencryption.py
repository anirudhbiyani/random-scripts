#!/usr/bin/env python

'''
Work in Progress - Checks for various entities like EC2, S3 and other other for Encryption
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20150312"

import boto, datetime, time
from boto.s3.connection import S3Connection
from boto.ec2 import EC2Connection
from boto.ec2.elb import ELBConnection

def main():
    filename = 'ebs-encrypt-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f=open(filename,'a')
    filename3 = 'snapshotencrypt-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f3=open(filename3,'a')
    f3.write('Date Time | S3 Path | Encrypted State' + '\n')
    ec2 = boto.ec2.connect_to_region('us-west-1')
    res = ec2.get_all_instances()
    instances = [i for r in res for i in r.instances]
    vol = ec2.get_all_volumes()
    f.write('Date Time | Attached Volume ID | Instance ID | Device Name | Encrypted State | Instance Name' + '\n' )
    for volumes in vol:
        if volumes.attachment_state() == 'attached':
            filter = {'block-device-mapping.volume-id':volumes.id}
            volumesinstance = ec2.get_all_instances(filters=filter)
            ids = [z for k in volumesinstance for z in k.instances]
            for s in ids:
                if (s.tags['Name'].startswith('ms-snx-saas-snypr')):
                    a = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + '|' + volumes.id + '|' + s.id + '|' + volumes.attach_data.device + '|' + str(volumes.encrypted) + '|' + s.tags['Name'] + '\n'
                    snapshots=ec2.get_all_snapshots(filters={'volume-id':volumes.id})
                    for snaps in snapshots:
                        f3.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + snaps.id + "|" + str(snaps.encrypted) + "|" + s.tags['Name'] + "|" + "\n")
                    f.write(a)
    f.close()
    f3.close()

    filename1 = 'elb-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f1=open(filename1,'a')
    f1.write('Date Time | ELB Name | Listener Port' + '\n')
    elb = boto.ec2.elb.connect_to_region('us-west-1')
    for lb in elb.get_all_load_balancers():
        f1.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + lb.name + '|' + str(lb.listeners[0][0]) + '\n')
    f1.close
    '''
    filename3 = 'snapshotencrypt-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f3=open(filename3,'a')
    f3.write('Date Time | S3 Path | Encrypted State' + '\n')
    connection=boto.ec2.connect_to_region('us-west-1')
    snapshots=connection.get_all_snapshots()
    for snaps in snapshots:
        f3.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + snaps.id + "|" + str(snaps.encrypted) + "|" + snaps.volumeid + "|" + "\n")
    f3.close
    '''
    filename2 = 's3encrypt-' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') + '.log'
    f2=open(filename2,'a')
    conn = S3Connection()
    bucket = conn.get_bucket('backup.securonix.net')
    f2.write('Date Time | S3 Path | Encrypted State' + '\n')
    for key in bucket.list():
        f2.write(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d  %H:%M:%S') + '|' + key.name.encode('utf-8') + '|' + str(key.encrypted) + '\n')
    f2.close

if __name__ == '__main__':
    main()
