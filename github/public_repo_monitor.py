import json
import requests
import os



def bitbucket_scan():
	Flag = False
	message = "The following repositories have been made public on Bitbucket: \n```"
	url = 'https://api.bitbucket.org/2.0/repositories/dreamplug-backend'
	results = json.loads(requests.get(url).text)
	if len(results['values']) > 0 or results['size'] > 0:
		for result in results['values']:
			Flag = True
			message += result['links']['self']['href'] + "\n"
	message += "```"
	if Flag:
		data = {'text': message}
		slack_url = os.environ.get('SLACK_URL')
		req = requests.post(slack_url, data=json.dumps(data))

def github_scan():
	Flag = False
	whitelist = [
	'cancel-workflow-action',
	'ARTIF',
	'synth-ios',
	"synth-android",
	]
	urls = [
		"https://api.github.com/orgs/CRED-dev/repos",
		"https://api.github.com/orgs/CRED-club/repos",
		]
	for url in urls:
		message = "The following repositories have been made public on Github: \n```"
		results = json.loads(requests.get(url).text)
		if len(results) > 0:
			for repo in results:
				if repo['name'] not in whitelist:
					Flag = True
					message+= repo['html_url'] + "\n"
		message+= "```"
		if Flag:
			data = {'text': message}
			slack_url = os.environ.get('SLACK_URL')
			req = requests.post(slack_url, data=json.dumps(data))

bitbucket_scan()
github_scan()