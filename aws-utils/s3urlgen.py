#!/usr/bin/env python

'''
This script generates a Pre-signed object URL to retrive an object from S3 bucket, without giving access to anyone.
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20170828"

import sys, boto

def main():
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""

    # Check for the number of arguments being passed and exit, if not according to usage.
    if len(sys.argv) != 3:
        print "Usage: ./" + sys.argv[0] + " Path of file as S3"
        print "Example - ./" + sys.argv[0] + "Uploads/Documents/test.txt"
        exit(1)

    # Variables that are needed and these will not change, unless explicitly said.
    bucketname = ""
    validity = 604800  #This is 7 days in seconds.

    # Connecting to the S3 API interface using the credentials for hkumar
    s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    # Generating the pre-signed URL for the uploaded zip file.
    URL = s3.generate_url(expires_in=long(validity), method='GET', bucket=bucketname, key=path, query_auth=True, force_http=False)
    print "The URL generated is - " + URL

if __name__ == "__main__":
        main()
