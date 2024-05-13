#!/usr/bin/env python

from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL, SUBTREE, AUTO_BIND_NO_TLS
import getpass, re

__author__ = "Aniruddha Biyani"
__version__ = "1.0.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "aniruddha.biyani@lithium.com"
__status__ = "InfoSec_Utilities"

def main():
    base_dn="DC=lithium, DC=local"

#    user = raw_input("Enter your username that you want to use to connect: ")
    user = 'aniruddha.biyani'
    pswd = getpass.getpass('Password:')
    usr="lithium.local\\"+user
    srv = Server('idcdc01.lithium.local', use_ssl=True, get_info=ALL)
    conn = Connection(srv, user=usr, password=pswd, authentication="NTLM")
    conn.bind()

    # This search is for AWS Production Accounts only.
    conn.search(search_base=base_dn, search_filter='(&(ObjectCategory=group)(CN=sso-aws*))', search_scope=SUBTREE, attributes=['member'])
    result = conn.entries
    for i in range(0,len(result)):
        a = result[i]
        a = str(a)
        m = re.findall('DN: CN=sso-aws-([A-Za-z .-]+),OU=SSO Apps', a)
        print m
#        if m:
#            print (m.groups())[0]
        u = re.findall('CN=([A-z. ]+),OU=.*,OU=Users,OU=Lithium,DC=lithium,DC=local',a)
        print ("\n".join(map(str, u)))
        print '-' * 40

if __name__ == '__main__':
    main()
