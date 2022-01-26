#!/usr/bin/env python

import openpyxl, getpass, re, requests, json
from ldap3 import Server, Connection, ALL_ATTRIBUTES, ALL, SUBTREE, AUTO_BIND_NO_TLS
from github import Github
from datetime import datetime, timedelta
from O365 import *

__author__ = "Aniruddha Biyani"
__version__ = "1.0.0"
__maintainer__ = "Aniruddha Biyani"
__email__ = "hi@anirudhbiyani.com"
__status__ = "InfoSec_Utilities"

def main():
    base_dn="DC=contoso, DC=local"

    user = raw_input("Enter your username that you want to use to connect: ")
    pswd = getpass.getpass('Password:')
    usr="contoso.local\\"+user
    srv = Server('server01.contoso.local', use_ssl=True, get_info=ALL)
    conn = Connection(srv, user=usr, password=pswd, authentication="NTLM")
    conn.bind()

    # This search is for AWS Production Accounts only.
    conn.search(search_base=base_dn, search_filter='(&(ObjectCategory=group)(CN=sso-aws*prod*))', search_scope=SUBTREE, attributes=['member'])
    result = conn.entries
    for i in range(0,len(result)):
        a = result[i]
        a = str(a)
        m = re.findall('DN: CN=sso-aws-([A-Za-z. -])+, OU=SSO Apps', a)
        print m
#        if m:
#            print (m.groups())[0]
        u = re.findall('CN=([A-z. ]+),OU=.*,OU=Users,OU=contoso,DC=contoso,DC=local',a)
        print ("\n".join(map(str, u)))
        print '-' * 40

    # BitBucket/Stash
    conn.search(search_base=base_dn, search_filter='(&(ObjectCategory=group)(CN=bitbucket*))', search_scope=SUBTREE, attributes=['member'])
    result = conn.entries
    for i in range(0,len(result)):
        a = result[i]
        a = str(a)
        if "OU=Distro Groups" not in a:
            m = re.search('DN: CN=([a-z-]+),OU=Atlassian,OU=Security Groups,OU=contoso,DC=contoso,DC=local', a)
            if m:
                print (m.groups())[0]
            u = re.findall('CN=([A-z. ]+),OU=.*,OU=Users,OU=contoso,DC=contoso,DC=local',a)
            print ("\n".join(map(str, u)))
            print '-' * 40
        else:
            continue
    conn.unbind()

    # GitHub
    g = Github(litoken)
    date = datetime.now() - timedelta(days=30)
    d = date.strftime('%Y-%m-%d')
    q = "org:contosotech pushed:>" + d
    repo = g.search_repositories(query="org:contosotech pushed:>2018-09-01")
    for r in repo:
        ro = g.get_repo(str(r)[22:-2])
        print ro.name
        collaborators = ro.get_contributors()
        for collaborator in collaborators:
            print collaborator.name, collaborator.login



    # SSH Access
    with open(sys.argv[1]) as f:
        for line in f:
            conn.search(search_base=base_dn, search_filter='(sAMAccountName=' + line +')', search_scope=SUBTREE, attributes=['displayName','manager'])
            result = conn.entries
            manager = re.search('manager: CN=([A-z. ]+),OU=', str(result))
            name = re.search('displayName: ([A-z. ]+)', str(result))
            if (manager == None):
                print (name.groups())[0] + ', ' + line.strip() + ', Not Available'
            elif (name == None):
                print 'Not Available, ' + line.strip() + ', ' + (manager.groups())[0]
            else:
                print (name.groups())[0] + ', ' + line.strip() + ', ' + (manager.groups())[0]

    # Email
    file='<Path to the attachment file>'
    o365_auth = ('aniruddha.biyani@contoso.com', pswd)
    a = Attachment(path=file)
    m = Message(auth=o365_auth)
    m.setRecipients('aniruddha.biyani@contoso.com')
    m.setSubject('I made an email script.')
    m.setBody('Talk to the computer, cause the human does not want to hear it any more.')
    m.attachments.append(a)
    m.sendMessage()

if __name__ == '__main__':
    main()
