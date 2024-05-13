#!/usr/bin/env python

from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL, SUBTREE, AUTO_BIND_NO_TLS
import getpass

def main():

	employee = "manu.matthew"
	usr="lithium.local\\aniruddha.biyani"
	pswd = getpass.getpass('Password:')
	base_dn="DC=lithium,DC=local"

	srv = Server('idcdc01.lithium.local', use_ssl=True, get_info=ALL)
	conn = Connection(srv, user=usr, password=pswd, authentication="NTLM")

	conn.bind()

	# conn.search(search_base=base_dn, search_filter='(sAMAccountName=' + employee + ')', search_scope=SUBTREE, attributes=ALL_ATTRIBUTES)
	conn.search(search_base=base_dn, search_filter='(&(ObjectCategory=group)(CN=sso-aws*))', search_scope=SUBTREE, attributes=['member'])

	print conn.entries

	conn.unbind()
if __name__=='__main__':
	main()
