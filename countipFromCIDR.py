#!/usr/bin/env python

from netaddr import *
import pprint

def main():
	count = 0
	f = open ('ipaddress.txt', 'rw+')
	for line in f:
		print line
		ip = IPNetwork(line)
		a = ip.size
		count = count + a
	print count

if __name__ == '__main__':
	main()
