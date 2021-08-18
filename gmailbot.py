from __future__ import print_function
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def getHeader(headers, name):
    for h in headers:
        if h['name'] == name:
            return h['value']
    return ("MISSING " + name.upper() + " HEADER")


def check(sender, subject):
    with open('keywords.json') as keyword_file:
        keywords = json.load(keyword_file)
        for label in keywords:
            for x in keywords[label]:
                if x.upper() in sender.upper() or x.upper() in subject.upper():
                    return label
    return "Other"

def labelEmails(service):
    size = 200
    tenthSize = size / 10
    results = service.users().messages().list(userId='me',maxResults=size).execute()
    messages = results.get('messages', [])
    labels = {}
    if not messages:
        print('No messages found.')
    else:
        count = 0
        for e in messages:
            if count % tenthSize == 0:
                print("-> " + str(int(count // tenthSize) * 10) + "% finished")
            if count == size - 1:
                print("-> 100% finished")
            message = service.users().messages().get(userId='me',id=e['id'],format='full').execute()
            headers = message['payload']['headers']
            sender = getHeader(headers, "From")
            subject = getHeader(headers,"Subject")
            label = check(sender, subject)
            if labels.get(label):
                labels.get(label).append(sender + " - " + subject)
            else:
                labels[label] = [(sender + " - " + subject)]
            count = count + 1

        return labels


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    input_code = 0
    print("This is E-Mail Bot! What would you like to do?")
    while input_code != 3:
        if input_code > 0 and input_code < 3:
            print("What else would you like to do?")
        print("(1) Label E-Mails")
        print("(2) Remove old E-Mails")
        print("(3) Quit Program")
        input_code = int(input("Enter input:"))
        if input_code == 1:
            labels = labelEmails(service)
            for l in labels:
                print(l)
                print("===============")
                for e in labels[l]:
                    print(e)
                print()
        if input_code > 3 or input_code < 1:
            print("\nInvalid input. Try again.")
    

            

if __name__ == '__main__':
    main()