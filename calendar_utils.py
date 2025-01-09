import json
import os
from datetime import datetime, timedelta, timezone
import pytz

import google.auth.exceptions
from main import *
from ai_utils import *

# ------------------------- Configuration ------------------------- #
# Define the scope for Google Calendar API access
SCOPES = ['https://www.googleapis.com/auth/calendar']


# ------------------------- Google Calendar Authentication ------------------------- #
def authenticate_google_calendar():
    """
        Authenticate the user with Google Calendar API.
        Handles token refresh and credential storage in 'token.json'.

        Returns:
            service: An authorized Google Calendar API service instance.
        """
    creds = None

    # Check if the token.json file with user credentials exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials are invalid or expired, prompt the user to re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError:
                print("Token has expired or being revoked. Removing token.json and re-authenticating")
                os.remove('token.json')  # Removes the invalid token file
                creds = None  # Resets creds to trigger re-authentication below
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Saves the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


# Initialize and build the service object
calendar_service = authenticate_google_calendar()


# ------------------------- Google Calendar Functions ------------------------- #
def get_upcoming_events(max_results=10):
    """
    Retrieve a list of upcoming events from the user's Google Calendar.

    Args:
        max_results (int): Maximum number of events to fetch.

    Returns:
        str: A formatted string of upcoming events.
    """
    # Get the current time in the correct timezone
    now = datetime.now(pytz.timezone('America/Denver')).isoformat()
    # print(now)

    # Fetch events from the current time onwards
    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=now,  # Only return events from the current time forward
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    print(type(events))
    if not events:
        return 'No upcoming events found.'

    # TODO: Add all events to a local JSON file
    with open('db.json', 'w') as db:
        json.dump(events, db, indent=4)

    response = []
    for event in events:
        start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        # response.append(f"{start}: {event['summary']}")
        start_time = start.strftime('%I:%M%p').lower()
        response.append(f"{event['summary']} at {start_time}")

    return "\n".join(response)


def add_event(gpt_output):
    """
    Add a new event to the user's Google Calendar.

    Args:
        gpt_output (dict): Event details parsed from user input.

    Returns:
        str: Confirmation message.
    """
    event_params = gpt_output["params"]
    # Set the duration to 1 hour if unstated by user
    if 'end' not in event_params:
        # Assuming start time is already set in event_params
        start_time = datetime.fromisoformat(event_params['start']['dateTime'])
        end_time = start_time + timedelta(hours=1)
        event_params['end'] = {'dateTime': end_time.isoformat()}
    event = calendar_service.events().insert(calendarId='primary', body=event_params).execute()

    # To append the new event to our local database
    with open('db.json', 'r') as db:
        data = json.load(db)
        data.append(event)
    with open('db.json', 'w') as db:
        json.dump(data, db, indent=4)

    return "Event created"


# TODO: Functions for delete_event and update_event
def delete_event(event_id):
    """
        Delete an event from Google Calendar.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            str: A confirmation message.
        """

    try:
        # Get the current event details
        event = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()

        # Delete the event
        calendar_service.events().delete(calendarId='primary', eventId=event_id).execute()

        print(f"Deleted {event.get('summary')} event")
        return f"{event.get('summary')} deleted successfully."
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Failed to delete event: {e}"


def update_event(event_id, updated_data):
    """
        Update an existing event in Google Calendar.

        Args:
            event_id (str): The ID of the event to update.
            updated_data (dict): A dictionary with the updated event details.

        Returns:
            str: A confirmation message.
        """
    try:
        # Get the current event details
        event = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()

        # Update the event with the new data
        event.update(updated_data)

        # Send the updated event to the API
        updated_event = calendar_service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

        print(f"Updated event: {updated_event.get('summary')}")
        return f"Event '{updated_event.get('summary')}' updated successfully."

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Failed to update event: {e}"
        pass

