import os
import json
import docker
import subprocess
import configparser
import requests
import logging
import hashlib
import json
import uuid
import time
import mysql.connector
from pathlib import Path
mydb2 = mysql.connector.connect(
 host="",
 user="",
 password="",
 database="",
 auth_plugin='mysql_native_password'
)
mycursor2 = mydb2.cursor()
mydb = mysql.connector.connect(
 host="",
 user="",
 password="",
 database="",
 auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor()
mycursor.execute('''create table IF NOT EXISTS issues (id VARCHAR(50),image_name VARCHAR(20),tool_name VARCHAR(20),issue VARCHAR(10000),hash VARCHAR(257),PRIMARY KEY (id));''')
#Output Location
TRIVY_RESULTS_LOCATION="/tmp/results/trivy/"
SECRET_SCANNER_LOCATION="/tmp/results/secret_scanner/"
class Scanner():
    def get_uuid():
        query = (f"SELECT uuid();")
        mycursor.execute(query)
        return mycursor.fetchall()
    def pull_unique_images():
        separator=", "
        uniqueimages = Utils.fetch_unique_images()
        for images in uniqueimages:
            try:
                imagename=separator.join(map(str, images)) 
                client = docker.from_env()
                print('Pulling',imagename)
                image = client.images.pull(imagename)
                Scanner.docker_scan(imagename)
                Scanner.secret_scan(imagename)
                Scanner.trivy_output(imagename)
                Scanner.remove_docker_image(imagename)
            except:
                print("Exception Faced During Pull",imagename)

    def docker_scan(image_name):
        tempimage=image_name
        tempresultspath=TRIVY_RESULTS_LOCATION
        newimagename=tempimage.replace("/", "-")
        Path(tempresultspath).mkdir(parents=True,exist_ok=True)
        if(os.path.isfile(os.path.join(tempresultspath,newimagename))==False):
                f=open(os.path.join(tempresultspath,newimagename),"x")
                f.close()
                subprocess.run("trivy image -f json -o %s %s" % (os.path.join(tempresultspath,newimagename),tempimage),shell=True)
        return None
    def remove_docker_image(image):
        client = docker.from_env()
        client.images.remove(image)
        print('Image Removed-',image)
    def secret_scanner_output(filename):
        f=open(filename,'r')
        json_output = json.load(f)
        f.close()
        if(json_output['Secrets']!= None):
            for secrets in json_output['Secrets']:
                if secrets['Severity']=='High':
                    issues={"image_name":json_output['Image Name']}
                    issues['Severity']=secrets['Severity']
                    issues['bug_type']=secrets['Matched Rule Name']
                    issues['filename']=secrets['Full File Name']
                    issues['vulnerable_code']=secrets['Matched Contents']
                    issues['description']=secrets['Matched Rule Name']
                    issues['Severity Score'] = secrets['Severity Score']
                    hash = hashlib.sha256(str(issues).encode('utf-8')).hexdigest()
                    uuid = Scanner.get_uuid()
                    Scanner.sent_result_to_db(uuid[0][0],json_output['Image Name'],'secret_scanner',str(json.dumps(issues).replace('"',"'")),hash)
    def secret_scan(image_name):
        tempimage=image_name
        images=tempimage.replace("/", "-")
        resultspath = SECRET_SCANNER_LOCATION
        Path(resultspath).mkdir(parents=True,exist_ok=True)
        FNULL = open(os.devnull, 'w')
        subprocess.run(f"docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v {resultspath}:/home/deepfence/output deepfenceio/secretscanning -json-filename '{images}.json' -image-name {image_name}",shell=True,stdout=FNULL)
        Scanner.secret_scanner_output(f"{resultspath}{images}.json")
        return None
    def trivy_output(image_name):
        issue={}
        imagefile=image_name.replace("/","-")
        if os.path.exists('%s' % (os.path.join(TRIVY_RESULTS_LOCATION))):
            with open('%s' % (os.path.join(TRIVY_RESULTS_LOCATION,imagefile)), encoding="utf8") as file:
                try:
                    Vulnerabilities = json.loads(file.read())
                except ValueError as e:
                    logging.debug('Error could not load the json file for the project: %s' % (imagefile))
                if(Vulnerabilities!= None): 
                    for Vulnerability in Vulnerabilities[0]['Vulnerabilities']:
                        image_name = Vulnerabilities[0]['Target']
                        try:
                            if Vulnerability['Severity'] == "HIGH" or Vulnerability['Severity'] == "CRITICAL":
                                issue['image_name'] = Vulnerabilities[0]['Target']
                                issue['image_type'] = Vulnerabilities[0]['Type']
                                issue['cve'] = Vulnerability['VulnerabilityID']
                                issue['package_name'] = Vulnerability['PkgName']
                                issue['installed_version'] = Vulnerability['InstalledVersion']
                                issue['severity'] = Vulnerability['Severity']
                                if "FixedVersion" in Vulnerability:
                                    issue['fixed_version'] = Vulnerability['FixedVersion']
                                    if "Description" in Vulnerability:
                                        issue['description'] = Vulnerability['Description']
                                        if "CVSS" in Vulnerability:
                                            if "nvd" in Vulnerability['CVSS']:
                                                if "V2Score" in Vulnerability['CVSS']['nvd']:
                                                    issue['cvss'] = Vulnerability['CVSS']['nvd']['V2Score']
                                hashforissue = hashlib.sha256(str(issue).encode('utf-8')).hexdigest()
                                uuid=Scanner.get_uuid()
                                if(Scanner.check_issue_exits(hashforissue)==False):
                                    Scanner.sent_result_to_db(uuid[0][0],imagefile,'trivy',str(json.dumps(issue).replace('"',"'")),hashforissue)
                        except Exception as e:
                            print(e)
                            logging.debug("Error parsing json file for project %s. Error: %s" % (imagefile, e))
        return  None
    def sent_result_to_db(uuid,image_name,tool_name,issue,issuehash):
        query = (f"INSERT INTO issues VALUES (\"{uuid}\",\"{image_name}\",\"{tool_name}\",\"{issue}\",\"{issuehash}\")")
        mycursor.execute(query)
        mydb.commit()
    def check_issue_exits(issuehash):
            hash_for_issue=issuehash
            results=("SELECT hash from issues WHERE hash='%s';" % (hash_for_issue))
            mycursor.execute(results)
            if(len(mycursor.fetchall())>0):
                    return True
            else:
                    return False
class Utils:
    def fetch_unique_images():
            mycursor2.execute("select DISTINCT image_name from asset_inventory where image_name IS NOT NULL AND image_name <> '';")
            myresult = mycursor2.fetchall()
            return myresult
if __name__ == '__main__':
        Scanner.pull_unique_images()