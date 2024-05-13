import imapclient
import datetime
import pyzmail
from jira import JIRA

# CONFIG FILE

# Enable Less Secure App Access for the GMAIL account
EMAIL_USERNAME = '' 
EMAIL_PASSWORD = ''

# Get JIRA API TOKEN from
# https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_SERVER = ''
JIRA_USERNAME = ''
JIRA_API_TOKEN = ''
JIRA_PROJECT = ''

def emailConnect():
    """
    Function to create imapObj and connect to Gmail 
    """
    imapObj = imapclient.IMAPClient('imap.gmail.com',ssl=True)
    imapObj.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
    return imapObj

def jiraConnect():
    """
    Function to create jira object and connect to Jira
    """
    jac = JIRA(config.JIRA_SERVER)
    jira = JIRA(basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN), options = {'server': config.JIRA_SERVER})
    return jira

def getEmails(imapObj):
    """
    Function to read the emails recieved since 'current data'-1 and return messages
    """
    date = datetime.date
    date_day = date.today() - datetime.timedelta(days=1)
    date_day = date.strftime(date_day,"%d-%b-%Y")
    select_info = imapObj.select_folder('INBOX',readonly =True)
    criteria = [["To",config.EMAIL_USERNAME],['SINCE', date_day]]
    msgs = imapObj.search(criteria)
    return msgs

def readEmail(imapObj, msg):
    """
    Function to return email and sender details for the given message id   
    """
    rawMessages = imapObj.fetch([msg], ['BODY[]'])
    message = pyzmail.PyzMessage.factory(rawMessages[msg][b'BODY[]'])
    emailBody = message.text_part.get_payload().strip().decode('utf-8')
    emailSender = message.get_addresses('from')[0][0]
    emailAddress = message.get_addresses('from')[0][1]
    emailSubject = message.get_subject()
    return emailSender, emailAddress, emailSubject, emailBody 

def createJiraIssue(issueReporter, issueReporterAddress, issueSummary, issueDescription):
    """
    Function to create a new Jira Issue based on the email and sender details
    """
    issue_dict = {                                  
        'project': config.JIRA_PROJECT,
        'summary': "[security@cred] - {}".format(issueSummary),
        'description': issueDescription + "\n\n*Reported By*: {} <{}>".format(issueReporter, issueReporterAddress),
        'issuetype': {'name': 'email'},
    }
    new_issue = jira.create_issue(fields=issue_dict)
    return new_issue

if __name__ == "__main__":
    imapObj = emailConnect()
    jira = jiraConnect()
    msgs = getEmails(imapObj)
    for msg in msgs:
        emailSender, emailAddress, emailSubject, emailBody = readEmail(imapObj, msg)
        if emailSubject == '' or emailBody == '' or len(emailBody) < 50:
            continue
        issue = createJiraIssue(emailSender, emailAddress, emailSubject, emailBody)
        print("[x] Created new issue: (KEY:{}, ID:{})".format(issue.key, issue.id))
    imapObj.logout()
