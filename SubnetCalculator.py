#!/usr/bin/env python

'''
Calculates the Network Range for a given CIDR. Currently, has issues with /32 network.
'''
__author__ = "Aniruddha Biyani"
__version__ = "1.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Production"
__date__ = "20150312"

import sys
# This script has issue with /32 Network
def main():
# Takes input cannot use input as that gives an error for slash and raw_input is not easy to manipulate.
    sys.stdout.write("Enter IP address in CIDR format: ")
    sys.stdout.flush()
    cidr = sys.stdin.readline()

# Splits the given input into the respective variables and their format.
    print("The input give is: " + cidr)
    ipaddr, mask = cidr.split('/')
    foctet, soctet, toctet, ooctet = ipaddr.split('.')
    baddr =  '{0:08b}'.format(int(foctet)) + '{0:08b}'.format(int(soctet)) + '{0:08b}'.format(int(toctet)) + '{0:08b}'.format(int(ooctet))

# Some validations
    if (foctet < 255) or (soctet < 255) or (toctet < 255) or (ooctet < 255) or (mask < 32):
            print "This is not a valid CIDR Notation. Please enter a valid one."
    else:
# Create the network in binary for the given subnet mask.
        temp, temp0 = '', ''
        for i in range(int(mask)):
            temp = temp + '1'
        for i in range(32 - int(mask)):
            temp0 = temp0 + '0'
        bmask = temp + temp0

# Converting the above string into binary and "AND"ing them to get the Nework Address
        baddr = int(baddr, base=2)
        bmask = int(bmask, base=2)
        bnaddr = '{0:032b}'.format(int(baddr & bmask))
        nfoctet, nsoctet, ntoctet, nooctet = int(bnaddr[0:8], base=2), int(bnaddr[8:16], base=2), int(bnaddr[16:24], base=2), int(bnaddr[24:32], base=2)
        print "The Network Address is " +str(nfoctet)+"."+str(nsoctet)+"."+str(ntoctet)+"."+str(nooctet)

# Printing the first host Address
        nooctet = nooctet + 1
        print "The First Host Address is " +str(nfoctet)+"."+str(nsoctet)+"."+str(ntoctet)+"."+str(nooctet)

# Converting the above string into binary and "AND"ing them to get the Broadcast Address
        temp, temp0 = '', ''
        for i in range(int(mask)):
            temp = temp + '0'
        for i in range(32 - int(mask)):
            temp0 = temp0 + '1'
        bnmask = temp + temp0
        bnmask = int(bnmask, base=2)
        bbaddr = '{0:032b}'.format(int(baddr | bnmask))
        nfoctet, nsoctet, ntoctet, nooctet = int(bbaddr[0:8], base=2), int(bbaddr[8:16], base=2), int(bbaddr[16:24], base=2), int(bbaddr[24:32], base=2)
        t = nooctet - 1
        print "The Last Host Address is " +str(nfoctet)+"."+str(nsoctet)+"."+str(ntoctet)+"."+str(t)
        print "The Broadcast Address is " +str(nfoctet)+"."+str(nsoctet)+"."+str(ntoctet)+"."+str(nooctet)

        print "The Number of host in the network are", 2**(32 - int(mask)) - 2

if __name__ == '__main__':
    main()
