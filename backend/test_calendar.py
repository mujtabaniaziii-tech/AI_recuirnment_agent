import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permission required: Calendar padhna aur events banana
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # Check karega agar pehle se login token majood hai
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Agar login nahi hai, toh browser open karega
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Browser khul raha hai, wahan apna Google account select karein...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Agli baar ke liye token save kar lega
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'  
        print("Fetching upcoming 10 events from your calendar...")
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print("No upcoming events found.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            
        print("\n✅ Connection Successful! Google Calendar is linked.")

    except Exception as e:
        print(f"\n❌ Error connecting to Google Calendar: {e}")

if __name__ == '__main__':
    main()