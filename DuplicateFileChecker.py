#!/usr/bin/env python

'''
Checks for duplicate files in a particular given directory based on SHA256 hashes.
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20150312"

import hashlib, os, pprint, thread
def main():
    print 'Please enter the absolute path in the input.'
    dirname = raw_input('Enter the directory in which you want to find the duplicates: ')
    dirname =  dirname.strip()
    allsizes = []
    duplicates = set()
    for (thisDir, subsHere, filesHere) in os.walk(dirname):
        for filename in filesHere:
#           if filename.endswith('.py'): This to check for a particular type of file.
            fullname = os.path.join(thisDir, filename)
#            fullsize = os.path.getsize(fullname)
            with open(fullname, "rb") as f:
                contents = f.read()
                sha2hash =  hashlib.sha256(contents).hexdigest()
            allsizes.append((fullname,  sha2hash))
#    pprint.pprint(allsizes) - Just a debug to list the whole "list".

    for intr in allsizes:
        for i in allsizes:
            if intr != i:
                if i[0] not in duplicates:
                    if intr[1] == i[1]:
                        print intr[0] + " is a duplicate of file " + i[0]
                        duplicates.add(intr[0])
if __name__ == '__main__':
    main()
