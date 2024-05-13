import os,subprocess
import mysql.connector
import hashlib
import uuid
import json
import logging 
from multiprocessing import Pool
import multiprocessing
 

mydb= mysql.connector.connect(                                                                                                                                           
 host="",                                                                                                       
 user="",
 password="",
 database="",
 auth_plugin='mysql_native_password'
)


mycursor = mydb.cursor()
mycursor.execute('''create table IF NOT EXISTS scanner_test3 (id VARCHAR(50),tool_name VARCHAR(20),reponame VARCHAR(20),issue json,hash VARCHAR(257),PRIMARY KEY (id));''')


REPO_LOCATION="/tmp/repos/"
GITLEAKS_RESULTS_LOCATION="/tmp/results/gitleaks/"
EARLYBIRD_SCANNER_LOCATION="/tmp/results/earlybird/"
config_toml="/tmp/config.toml"


def gitleaksscan(repos):
    pool = Pool(processes=multiprocessing.cpu_count())
    res = pool.map(gitleakscanner, repos)
    pool.close()
    pool.join()
    return

def earlybirdscan(repos):
    pool = Pool(processes=multiprocessing.cpu_count())
    res = pool.map(earlybirdscanner, repos)
    pool.close()
    pool.join()
    return

def scanall():    
    d=os.listdir(REPO_LOCATION)
    earlybirdscan(d)
    gitleaksscan(d)
    return

def gitleakscanner(reponame):    
    d = os.path.join(REPO_LOCATION, reponame)
    if os.path.isdir(d):
        repopath=os.path.join(REPO_LOCATION,reponame)
        gitleakresultpath=os.path.join(GITLEAKS_RESULTS_LOCATION,reponame)
        subprocess.run("gitleaks -r %s/ -o %s -c=%s" % (repopath,gitleakresultpath,config_toml),shell=True)
        gitleakparser(gitleakresultpath,reponame)
    return

def earlybirdscanner(reponame):
    d = os.path.join(REPO_LOCATION, reponame)
    if os.path.isdir(d):
        repopath=os.path.join(REPO_LOCATION,reponame)
        earlybirdresultpath=os.path.join(EARLYBIRD_SCANNER_LOCATION,reponame)
        subprocess.run("go-earlybird -path %s/ -file %s -format json " % (repopath,earlybirdresultpath),shell=True)
        earlybirdparser(earlybirdresultpath,reponame)
    return

def gitleakparser(filename,reponame):
    issue={}
    print(filename)
    if os.path.exists('%s' % (os.path.join(filename))):
        with open('%s' % (os.path.join(filename)), encoding="utf8") as file:
            try:
                secrets = json.loads(file.read())
                print(secrets)
                if(secrets!= None): 
                    for secret in secrets:
                        issue["secret_value"]=secret["line"]
                        issue["secret_type"]=secret["rule"]
                        issue["linenumber"]=secret["lineNumber"]
                        issue["commit"]=secret["commit"]
                        issue["filename"]=secret["file"]
                        issue["reponame"]=reponame
                        hashforissue = hashlib.sha256(str(issue).encode('utf-8')).hexdigest()
                        id=uuid.uuid4().hex
                        tool_name="gitleaks"
                        try:
                            if(check_issue_exits(hashforissue)==False):
                                sendtodb(id,tool_name,reponame,json.dumps(issue),hashforissue)
                        except:
                            print("cant send to db")
                            pass     
            except ValueError as e:
                logging.debug('Error could not load the json file for the project: %s' % (filename))
    return 

def earlybirdparser(filename,reponame):
    issue={}
    print(filename)
    if os.path.exists('%s' % (os.path.join(filename))):
        with open('%s' % (os.path.join(filename)), encoding="utf8") as file:
            try:
                secrets = json.loads(file.read())
                if(secrets!= None):
                    if secrets["hits"] is not None: 
                        for secret in secrets["hits"]:
                            issue["secret_value"]=secret["match_value"]
                            issue["secret_type"]=secret["caption"]
                            issue["linenumber"]=secret["line"]
                            issue["filename"]=secret["filename"]
                            issue["reponame"]=reponame
                            hashforissue = hashlib.sha256(str(issue).encode('utf-8')).hexdigest()
                            id=uuid.uuid4().hex
                            tool_name="earlybird"
                            try:
                                if(check_issue_exits(hashforissue)==False):
                                    sendtodb(id,tool_name,reponame,json.dumps(issue),hashforissue)
                            except:
                                pass     
            except ValueError as e:
                logging.debug('Error could not load the json file for the project: %s' % (filename))
    return 

def sendtodb(uuid,tool_name,reponame,issue,issuehash):
    query = (f"INSERT INTO scanner_test3 VALUES (\"{uuid}\",\"{tool_name}\",\"{reponame}\",\'{issue}\',\"{issuehash}\")")
    mycursor.execute(query)
    mydb.commit()

def check_issue_exits(issuehash):
    hash_for_issue=issuehash
    results=("SELECT hash from scanner_test3 WHERE hash='%s';" % (hash_for_issue))
    mycursor.execute(results)
    if(len(mycursor.fetchall())>0):
        return True
    else:
        return False

if __name__ == '__main__':
    scanall()
