import os
import subprocess
import requests
import json
import shutil

base_path = "/home/ubuntu/"
user_file="users.txt"
filepath=base_path+user_file
TOKEN = ""
repos_url = "https://api.github.com/users/{{USERNAME}}/repos"
slack_webhook_url=""

from_date_to_scan='2019-01-01'

def get_json(url):
    response = requests.get(url, auth=("jaiswalakshansh", TOKEN))
    response.raise_for_status()
    return response.json()

def send_to_slack(repo,secret,file_name,value,commit,username):
    link="https://github.com/"+username+"/"+repo+"/blob/"+commit+"/"+file_name
    text = "`A %s is found with value %s` \n```Link: %s```" % (
        secret, value, link)
    payload = {'text': text}
    requests.post(slack_webhook_url, data=json.dumps(payload))    

def main():
    with open(filepath) as f:
        usernames = [username.strip() for username in f]
    for username in usernames:
        repos_url_ = repos_url.replace("{{USERNAME}}", username)
        repos = get_json(repos_url_)
        orin=os.getcwd()
        try:
            os.makedirs(username)
        except OSError:
            print(f"Error: Unable to create directory '{username}'")
            pass
        os.chdir(username)
        for repo in repos:
            if not repo["fork"]:
                if repo['created_at'] >= from_date_to_scan:
                    clone_url = repo["clone_url"]
                    subprocess.run(["git", "clone", clone_url])

        cwd = os.getcwd()
        dirs = [d.name for d in os.scandir(cwd) if d.is_dir()]

        for d in dirs:
            os.chdir(d)
            pp=os.getcwd()
            print(f"Scanning directory: {pp}")
            subprocess.run(["gitleaks", "detect", "--source", ".", "-v", "-f", "json", "-r", f"{d}.json"])
            filen=d+".json"
            print(filen)
            with open(filen) as ff:
                k=json.load(ff)
                for all in k:
                    description=all["Description"]
                    file_name=all["File"]
                    value=all["Secret"]
                    commit=all["Commit"]
                    send_to_slack(d,description,file_name,value,commit,username)
                os.chdir(cwd)    
        os.chdir(orin)
        try:
            shutil.rmtree(username)
        except OSError:
            print(OSError)
            print(f"Error: Unable to remove directory '{username}'")
            continue        
        
main()
