#!/usr/bin/env python

import openpyxl, getpass, re, requests, json
from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL, SUBTREE, AUTO_BIND_NO_TLS

# To fetch all the active directory groups that the user is part of

__author__ = "Aniruddha Biyani"
__version__ = "1.0.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "contact@anirudhbiyani.com"
__status__ = "Active"

def main():
    base_dn="OU=Users,DC=Contoso, DC=local"
    domain = "contoso.local\\"
    domainController = ""
    employeeName =""
    user = raw_input("Enter your username that you want to use to connect: ")
    pswd = getpass.getpass('Password:')
    usr=domain+user
    srv = Server(domainController, use_ssl=True, get_info=ALL)
    conn = Connection(srv, user=usr, password=pswd, authentication="NTLM")
    conn.bind()

    conn.search(search_base=base_dn, search_filter='(sAMAccountName='+ employeeName +')', search_scope=SUBTREE, attributes='*')
    result = conn.entries

    for i in range(0,len(result)):
        a = result[i]
        a = str(a)
        m = re.search('DN: CN=(.*),OU=Internal,OU=Distro Groups,OU=Users,DC=Contoso,DC=local', a)
        # print (m.groups())[0]
        if m == None:
            print a
        else:
            print m.groups()

    conn.unbind()

if __name__ == '__main__':
    main()
