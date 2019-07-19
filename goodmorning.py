from __future__ import print_function
import schedule
import time
import datetime
import pickle
import os.path
from twilio.rest import Client
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_events():
    print('in func')
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now().isoformat() + 'Z'
    # calculate tomorrows datetime for range to request
    tomorrow = str(datetime.datetime.now()+datetime.timedelta(days=1))+'Z'
    tomorrow_date = tomorrow.split(' ')
    tomorrow = tomorrow_date[0]+'T'+tomorrow_date[1]

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime', timeMax=tomorrow).execute()

    events = events_result.get('items', [])

    msg = ""

    if not events:
        msg += "Enjoy your day off. No events in your calendar."
    else:
        msg += "Good morning. Here are your upcoming events for " + now.split("T")[0]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start.split("-")[2]
            start = start.split("T")[1][:-3]
            end = event['end'].get('dateTime', event['end'].get('date'))
            end = end.split("-")[2]
            end = end.split("T")[1][:-3]
            msg += start + "-" + end + " " + event['summary'] + "\n"
            #print(start, "-", end, event['summary'])

    # Your Account SID from twilio.com/console
    account_sid = ""
    # Your Auth Token from twilio.com/console
    auth_token  = ""
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+", 
        from_="+17122922649",
        body=msg)
    
    #print(message.sid)


def main(): 
    schedule.every().day.at("06:00").do(get_events)
    while True:
        print('run pending')
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()
